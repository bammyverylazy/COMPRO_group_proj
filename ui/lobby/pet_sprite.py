from __future__ import annotations

import itertools
import math
import random
import time
from functools import lru_cache
from pathlib import Path, PurePosixPath

import flet as ft

from app.dto import PetDTO


Rect = tuple[float, float, float, float]
ASSETS_DIR: Path = Path(__file__).resolve().parents[2] / "assets"

_uid_counter = itertools.count(1)


@lru_cache(maxsize=None)
def asset_exists(path: str) -> bool:
    return (ASSETS_DIR / path).is_file()


class PetSprite:
    BASE_SIZE: int = 170
    DEFAULT_SPEED: float = 40.0
    MIN_REST_SEC: float = 1.0
    MAX_REST_SEC: float = 3.0
    ARRIVAL_DISTANCE: float = 1.0
    FOOT_RATIO: float = 0.75
    SIDE_RATIO: float = 0.3
    BODY_RATIO: float = 0.4
    PATH_STEP: float = 8.0
    TARGET_TRIES: int = 40

    LEAD_SEC: float = 0.05
    MAX_STEP_SEC: float = 0.05
    ARRIVE_GRACE: float = 0.08

    HEADING_SIDE: str = "side"
    HEADING_UP: str = "up"
    HEADING_DOWN: str = "down"

    def __init__(
        self,
        pet: PetDTO,
        x: float,
        y: float,
        speed: float = DEFAULT_SPEED,
    ) -> None:
        self.pet = pet
        self.x = x
        self.y = y
        self.speed = speed
        self.uid = next(_uid_counter)

        self.target_x = x
        self.target_y = y

        self.start_x = x
        self.start_y = y
        self.trip_elapsed = 0.0
        self.trip_duration = 0.0

        now = time.monotonic()
        self.last_update = now
        self.rest_until = now + random.uniform(0.0, self.MAX_REST_SEC)

        self.facing_left = False
        self.heading: str = self.HEADING_SIDE

        self.image: ft.Image | None = None
        self.container: ft.Container | None = None
        self.moving = False
        self._last_src: str = ""

        self._anim_move = ft.Animation(
            duration=int(self.LEAD_SEC * 1000), curve=ft.AnimationCurve.LINEAR
        )
        self._anim_snap = ft.Animation(duration=1, curve=ft.AnimationCurve.LINEAR)

    @property
    def size(self) -> float:
        return self.BASE_SIZE * self.pet.scale

    @property
    def sprite_directory(self) -> str:
        path = PurePosixPath(self.pet.species.sprite_path)
        return str(path.parent)

    @property
    def sprite_name(self) -> str:
        path = PurePosixPath(self.pet.species.sprite_path)
        return path.parent.name

    @property
    def feet_y(self) -> float:
        return self.y + (self.size * self.FOOT_RATIO)

    def _sprite_path(self, filename: str) -> str:
        return f"{self.sprite_directory}/{filename}"

    def _resolve_asset(self, relative_path: str) -> str | None:
        if asset_exists(relative_path):
            return relative_path

        p = PurePosixPath(relative_path)
        ext = p.suffix
        alt_ext = ext.upper() if ext.islower() else ext.lower()
        alt_path = str(p.with_suffix(alt_ext))

        if asset_exists(alt_path):
            return alt_path

        return None

    def _front_path(self) -> str:
        path = self._sprite_path(f"{self.sprite_name}_front.PNG")
        resolved = self._resolve_asset(path)
        return resolved if resolved else path

    def _wanted_sprite_path(self) -> str:
        if not self.moving:
            return self._front_path()

        if self.heading == self.HEADING_SIDE:
            side = "left" if self.facing_left else "right"
            return self._sprite_path(f"{self.sprite_name}_{side}.PNG")

        if self.heading == self.HEADING_UP:
            return self._sprite_path(f"{self.sprite_name}_move_back.GIF")

        return self._sprite_path(f"{self.sprite_name}_move_forward.GIF")

    def _current_sprite_path(self) -> str:
        wanted = self._wanted_sprite_path()
        resolved = self._resolve_asset(wanted)

        if resolved:
            return resolved

        return self._front_path()

    def build(self) -> ft.Control:
        sprite_path = self._current_sprite_path()
        self._last_src = sprite_path

        self.image = ft.Image(
            src=sprite_path,
            width=self.size,
            height=self.size,
            fit=ft.BoxFit.CONTAIN,
            gapless_playback=True,
        )

        self.container = ft.Container(
            content=self.image,
            left=self.x,
            top=self.y,
            key=f"pet-{self.uid}",
            animate_position=self._anim_snap,
        )

        return self.container

    def _bounds(self, area: Rect) -> Rect:
        left, top, right, bottom = area
        min_x = left - self.size * self.SIDE_RATIO
        max_x = max(min_x, right - self.size * (1 - self.SIDE_RATIO))
        min_y = top - self.size * self.FOOT_RATIO
        max_y = max(min_y, bottom - self.size * self.FOOT_RATIO)
        return min_x, max_x, min_y, max_y

    def _feet(self, x: float, y: float) -> tuple[float, float]:
        return x + self.size / 2, y + self.size * self.FOOT_RATIO

    def _blocked(self, x: float, y: float, obstacles: list[Rect]) -> bool:
        feet_x, feet_y = self._feet(x, y)
        half_body = self.size * self.BODY_RATIO / 2
        for left, top, right, bottom in obstacles:
            if left - half_body <= feet_x <= right + half_body and top <= feet_y <= bottom:
                return True
        return False

    def _path_clear(self, x: float, y: float, obstacles: list[Rect]) -> bool:
        distance = math.hypot(x - self.x, y - self.y)
        steps = max(1, int(distance / self.PATH_STEP))
        for step in range(1, steps + 1):
            ratio = step / steps
            if self._blocked(self.x + (x - self.x) * ratio, self.y + (y - self.y) * ratio, obstacles):
                return False
        return True

    def choose_target(self, area: Rect, obstacles: list[Rect], check_path: bool = True) -> None:
        min_x, max_x, min_y, max_y = self._bounds(area)
        escaping = self._blocked(self.x, self.y, obstacles)
        for _ in range(self.TARGET_TRIES):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            if self._blocked(x, y, obstacles):
                continue
            if check_path and not escaping and not self._path_clear(x, y, obstacles):
                continue
            self.target_x = x
            self.target_y = y
            return
        self.target_x = self.x
        self.target_y = self.y

    def place(self, area: Rect, obstacles: list[Rect]) -> None:
        self.choose_target(area, obstacles, check_path=False)
        self.x = self.target_x
        self.y = self.target_y

    def move_feet_to(self, feet_x: float, feet_y: float) -> None:
        self.x = feet_x - self.size / 2
        self.y = feet_y - self.size * self.FOOT_RATIO

    def keep_inside(self, area: Rect, obstacles: list[Rect]) -> None:
        min_x, max_x, min_y, max_y = self._bounds(area)
        self.moving = False
        self.x = min(max(self.x, min_x), max_x)
        self.y = min(max(self.y, min_y), max_y)
        if self._blocked(self.x, self.y, obstacles):
            self.place(area, obstacles)
        self.target_x = self.x
        self.target_y = self.y
        self.rest_until = 0.0
        self.last_update = time.monotonic()
        self._push_snap()

    def _lock_heading(self, dx: float, dy: float) -> None:
        if abs(dx) >= abs(dy):
            self.heading = self.HEADING_SIDE
            self.facing_left = dx < 0
        elif dy < 0:
            self.heading = self.HEADING_UP
        else:
            self.heading = self.HEADING_DOWN

    def _position_at(self, elapsed: float) -> tuple[float, float]:
        if self.trip_duration <= 0:
            return self.target_x, self.target_y
        progress = min(1.0, max(0.0, elapsed / self.trip_duration))
        return (
            self.start_x + (self.target_x - self.start_x) * progress,
            self.start_y + (self.target_y - self.start_y) * progress,
        )

    def update(self, now: float, area: Rect, obstacles: list[Rect]) -> bool:
        dt = min(max(now - self.last_update, 0.0), self.MAX_STEP_SEC)
        self.last_update = now

        if self.moving:
            self.trip_elapsed += dt

            if self.trip_elapsed >= self.trip_duration + self.ARRIVE_GRACE:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
                self.rest_until = now + random.uniform(self.MIN_REST_SEC, self.MAX_REST_SEC)
                return self._push_src()

            self.x, self.y = self._position_at(self.trip_elapsed)

            if self.trip_elapsed < self.trip_duration:
                return self._push_position()
            return False

        if now < self.rest_until:
            return False

        return self._start_trip(now, area, obstacles)

    def _push_position(self) -> bool:
        if self.container is None:
            return False
        ahead_x, ahead_y = self._position_at(self.trip_elapsed + self.LEAD_SEC)
        self.container.animate_position = self._anim_move
        self.container.left = ahead_x
        self.container.top = ahead_y
        return True

    def _start_trip(self, now: float, area: Rect, obstacles: list[Rect]) -> bool:
        self.choose_target(area, obstacles)

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)

        if distance <= self.ARRIVAL_DISTANCE:
            self.rest_until = now + random.uniform(self.MIN_REST_SEC, self.MAX_REST_SEC)
            return False

        self._lock_heading(dx, dy)
        self.start_x = self.x
        self.start_y = self.y
        self.trip_elapsed = 0.0
        self.trip_duration = distance / max(self.speed, 1e-6)
        self.moving = True

        if self.container is None or self.image is None:
            return False

        self._push_src()
        return self._push_position()

    def _push_src(self) -> bool:
        if self.image is None:
            return False
        src = self._current_sprite_path()
        if src == self._last_src:
            return False
        self.image.src = src
        self._last_src = src
        return True

    def _push_snap(self) -> None:
        if self.container is None or self.image is None:
            return
        self.container.animate_position = self._anim_snap
        self.container.left = self.x
        self.container.top = self.y
        self._push_src()