from __future__ import annotations

import math
import random
from pathlib import PurePosixPath

import flet as ft

from app.dto import PetDTO


class PetSprite:
    BASE_SIZE: int = 64
    DEFAULT_SPEED: float = 40.0
    MIN_REST_SEC: float = 1.0
    MAX_REST_SEC: float = 3.0
    ARRIVAL_DISTANCE: float = 1.0

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

    def _current_sprite_path(self) -> str:
        if not self.moving:
            return self._sprite_path(f"{self.sprite_name}_front.PNG")

        if abs(self.target_x - self.x) >= abs(self.target_y - self.y):
            if self.facing_left:
                return self._sprite_path(f"{self.sprite_name}_left.PNG")

            return self._sprite_path(f"{self.sprite_name}_right.PNG")

        if self.target_y < self.y:
            return self._sprite_path(
                f"{self.sprite_name}_move_back.GIF"
            )

        return self._sprite_path(
            f"{self.sprite_name}_move_forward.GIF"
        )

    def build(self) -> ft.Control:
        sprite_path = self._current_sprite_path()

        self.image = ft.Image(
            src=sprite_path,
            width=self.size,
            height=self.size,
            fit="contain",
        )

        self.container = ft.Container(
            content=self.image,
            left=self.x,
            top=self.y,
        )

        return self.container

    def choose_target(
        self,
        width: float,
        height: float,
    ) -> None:
        self.target_x = random.uniform(
            0,
            max(0, width - self.size),
        )

        self.target_y = random.uniform(
            0,
            max(0, height - self.size),
        )

    def update(
        self,
        dt: float,
        width: float,
        height: float,
    ) -> None:
        if self.rest_sec > 0:
            self.rest_sec -= dt
            self.moving = False

            if self.rest_sec <= 0:
                self.choose_target(width, height)

            self._refresh_visual()
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= self.ARRIVAL_DISTANCE:
            self.x = self.target_x
            self.y = self.target_y
            self.rest_sec = random.uniform(
                self.MIN_REST_SEC,
                self.MAX_REST_SEC,
            )
            self.moving = False
            self._refresh_visual()
            return

        if dx < 0:
            self.facing_left = True
        elif dx > 0:
            self.facing_left = False

        self.moving = True

        move_distance = min(
            self.speed * dt,
            distance,
        )

        self.x += (dx / distance) * move_distance
        self.y += (dy / distance) * move_distance

        self._refresh_visual()

    def _refresh_visual(self) -> None:
        if self.container is None or self.image is None:
            return

        self.container.left = self.x
        self.container.top = self.y
        self.image.src = self._current_sprite_path()