from __future__ import annotations

import asyncio

import flet as ft

from app.dto import PetDTO
from ui.core.base_widget import BaseWidget
from ui.lobby.pet_sprite import PetSprite


class SanctuaryScene(BaseWidget):
    BACKGROUND_PATH: str = "backgrounds/lobby_background.png"

    def __init__(
        self,
        width: float,
        height: float,
        fps: int = 20,
    ) -> None:
        super().__init__()

        self.width = width
        self.height = height
        self.fps = fps

        self.sprites: list[PetSprite] = []
        self.running = False
        self.stack: ft.Stack | None = None

    def build(self) -> ft.Control:
        self.stack = ft.Stack(
            width=self.width,
            height=self.height,
            controls=self._layers(),
        )
        return self.stack

    def load(self, pets: list[PetDTO]) -> None:
        self.sprites = []

        for pet in pets:
            sprite = PetSprite(pet=pet, x=0, y=0)
            sprite.choose_target(self.width, self.height)
            sprite.x = sprite.target_x
            sprite.y = sprite.target_y
            self.sprites.append(sprite)

        if self.stack is not None:
            self.stack.controls = self._layers()
            self.refresh()

    def start(self, page: ft.Page) -> None:
        if self.running:
            return

        self.running = True
        page.run_task(self._loop)

    def stop(self) -> None:
        self.running = False

    async def _loop(self) -> None:
        dt = 1.0 / self.fps

        while self.running:
            self.tick(dt)
            await asyncio.sleep(dt)

    def tick(self, dt: float) -> None:
        if self.stack is None:
            return

        for sprite in self.sprites:
            sprite.update(
                dt=dt,
                width=self.width,
                height=self.height,
            )

        self.refresh()

    def _layers(self) -> list[ft.Control]:
        background = ft.Image(
            src=self.BACKGROUND_PATH,
            width=self.width,
            height=self.height,
            fit=ft.BoxFit.FILL,
        )
        return [background, *[sprite.build() for sprite in self.sprites]]
