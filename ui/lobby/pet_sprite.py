from __future__ import annotations

import math
import random
from functools import lru_cache
from pathlib import Path, PurePosixPath

import flet as ft

from app.dto import PetDTO


Rect = tuple[float, float, float, float]
ASSETS_DIR: Path = Path(__file__).resolve().parents[2] / "assets"


@lru_cache(maxsize=None)
def asset_exists(path: str) -> bool:
    return (ASSETS_DIR / path).is_file()


class PetSprite:
    BASE_SIZE: int = 220
    DEFAULT_SPEED: float = 40.0
    MIN_REST_SEC: float = 1.0
    MAX_REST_SEC: float = 3.0
    ARRIVAL_DISTANCE: float = 1.0
    FOOT_RATIO: float = 0.75
    SIDE_RATIO: float = 0.3
    BODY_RATIO: float = 0.4
    PATH_STEP: float = 8.0
    TARGET_TRIES: int = 40

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

        self.target_x = x
        self.target_y = y

        self.rest_sec = 0.0
        self.facing_left = False

        self.image: ft.Image | None = None
        self.container: ft.Container | None = None
        self.moving = False

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

    def _sprite_path(self, filename: str) -> str:
        return f"{self.sprite_directory}/{filename}"

    def _front_path(self) -> str:
        return self._sprite_path(
            f"{self.sprite_name}_front.PNG"
        )

    def _wanted_sprite_path(self) -> str:
        if not self.moving:
            return self._front_path()

        if abs(self.target_x - self.x) >= abs(self.target_y - self.y):
            if self.facing_left:
                return self._sprite_path(
                    f"{self.sprite_name}_left.PNG"
                )

            return self._sprite_path(
                f"{self.sprite_name}_right.PNG"
            )

        if self.target_y < self.y:
            return self._sprite_path(
                f"{self.sprite_name}_move_back.GIF"
            )

        return self._sprite_path(
            f"{self.sprite_name}_move_forward.GIF"
        )

    def _current_sprite_path(self) -> str:
        path = self._wanted_sprite_path()

        if asset_exists(path):
            return path

        return self._front_path()

    def build(self) -> ft.Control:
        sprite_path = self._current_sprite_path()

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

    def keep_inside(self, area: Rect, obstacles: list[Rect]) -> None:
        min_x, max_x, min_y, max_y = self._bounds(area)
        self.x = min(max(self.x, min_x), max_x)
        self.y = min(max(self.y, min_y), max_y)
        self.choose_target(area, obstacles)
        self._refresh_visual()

    def update(self, dt: float, area: Rect, obstacles: list[Rect]) -> None:
        if self.rest_sec > 0:
            self.rest_sec -= dt
            self.moving = False
            if self.rest_sec <= 0:
                self.choose_target(area, obstacles)
            self._refresh_visual()
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= self.ARRIVAL_DISTANCE:
            self.x = self.target_x
            self.y = self.target_y
            self.rest_sec = random.uniform(self.MIN_REST_SEC, self.MAX_REST_SEC)
            self.moving = False
            self._refresh_visual()
            return

        if dx < 0:
            self.facing_left = True
        elif dx > 0:
            self.facing_left = False

        self.moving = True
        move_distance = min(self.speed * dt, distance)
        self.x += (dx / distance) * move_distance
        self.y += (dy / distance) * move_distance
        self._refresh_visual()

    def _refresh_visual(self) -> None:
        if self.container is None or self.image is None:
            return

        self.container.left = self.x
        self.container.top = self.y

        self.image.src = self._current_sprite_path()