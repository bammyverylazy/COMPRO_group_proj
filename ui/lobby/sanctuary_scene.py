from __future__ import annotations

import asyncio
import time

import flet as ft

from app.dto import PetDTO
from ui.core.base_widget import BaseWidget
from ui.lobby.pet_sprite import PetSprite, Rect


class SanctuaryScene(BaseWidget):
    BACKGROUND_WIDTH: float = 4732
    BACKGROUND_HEIGHT: float = 3192
    FLOOR_TOP_RATIO: float = 0.53
    TABLES: tuple[Rect, ...] = (
        (0.0, 0.473, 0.071, 0.646),
        (0.24, 0.447, 0.408, 0.697),
        (0.642, 0.447, 0.884, 0.702),
        (0.888, 0.456, 1.0, 0.665),
    )

    MIN_FPS: int = 30

    REORDER_MARGIN: float = 8.0

    REORDER_INTERVAL: float = 0.5

    ENABLE_REORDER: bool = True

    AUTO_MEASURE: bool = True

    def __init__(
        self,
        width: float,
        height: float,
        top: float = 0.0,
        bottom: float = 0.0,
        fps: int = 20,
    ) -> None:
        super().__init__()
        self.width = width
        self.height = height
        self.top = top
        self.bottom = bottom
        self.fps = max(fps, self.MIN_FPS)
        self.sprites: list[PetSprite] = []
        self.running = False
        self.stack: ft.Stack | None = None
        self._last_reorder = 0.0

    def build(self) -> ft.Control:
        self.stack = ft.Stack(controls=self._layers(), expand=True)
        if not self.AUTO_MEASURE:
            return self.stack
        try:
            return ft.Container(
                content=self.stack,
                expand=True,
                on_size_change=self._on_size_change,
            )
        except TypeError:
            return self.stack

    def _on_size_change(self, e) -> None:
        try:
            width = float(getattr(e, "width", None))
            height = float(getattr(e, "height", None))
        except (TypeError, ValueError):
            return
        if width <= 0 or height <= 0:
            return
        try:
            self.resize(width, height)
        except RuntimeError:
            pass

    def resize(self, width: float, height: float) -> None:
        if abs(width - self.width) < 0.5 and abs(height - self.height) < 0.5:
            return

        old_width, old_height = self.width, self.height
        fractions = [
            self._to_fraction(
                sprite.x + sprite.size / 2, sprite.feet_y, old_width, old_height
            )
            for sprite in self.sprites
        ]

        self.width = width
        self.height = height
        area = self._area()
        obstacles = self._obstacles()
        for sprite, (fx, fy) in zip(self.sprites, fractions):
            screen_x, screen_y = self._to_screen(fx, fy)
            sprite.move_feet_to(screen_x, screen_y)
            sprite.keep_inside(area, obstacles)
        self.refresh()

    def load(self, pets: list[PetDTO]) -> None:
        self.sprites = []
        area = self._area()
        obstacles = self._obstacles()
        for pet in pets:
            sprite = PetSprite(pet=pet, x=0, y=0)
            sprite.place(area, obstacles)
            self.sprites.append(sprite)

        self.sprites.sort(key=lambda s: s.feet_y)

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
        interval = 1.0 / self.fps
        next_at = time.perf_counter()
        while self.running:
            try:
                self.tick()
            except RuntimeError:
                self.running = False
                return
            next_at += interval
            delay = next_at - time.perf_counter()
            if delay < 0:
                next_at = time.perf_counter()
                delay = 0.0
            await asyncio.sleep(delay)

    def tick(self, dt: float | None = None) -> None:
        if self.stack is None:
            return

        now = time.monotonic()
        area = self._area()
        obstacles = self._obstacles()

        dirty = False
        for sprite in self.sprites:
            if sprite.update(now, area, obstacles):
                dirty = True

        if self.ENABLE_REORDER and now - self._last_reorder >= self.REORDER_INTERVAL:
            self._last_reorder = now
            if self._resort():
                self.stack.controls = [
                    s.container for s in self.sprites if s.container is not None
                ]
                dirty = True

        if dirty:
            self.refresh()

    def _resort(self) -> bool:
        changed = False
        sprites = self.sprites
        margin = self.REORDER_MARGIN
        for i in range(1, len(sprites)):
            j = i
            while j > 0 and sprites[j - 1].feet_y > sprites[j].feet_y + margin:
                sprites[j - 1], sprites[j] = sprites[j], sprites[j - 1]
                j -= 1
                changed = True
        return changed

    def _area(self) -> tuple[float, float, float, float]:
        floor_bottom = max(self.top, self.height - self.bottom)
        floor_top = min(max(self.top, self._floor_top()), floor_bottom)
        return 0.0, floor_top, self.width, floor_bottom

    def _floor_top(self) -> float:
        return self._to_screen(0.0, self.FLOOR_TOP_RATIO)[1]

    def _obstacles(self) -> list[Rect]:
        rects: list[Rect] = []
        for left, top, right, bottom in self.TABLES:
            x1, y1 = self._to_screen(left, top)
            x2, y2 = self._to_screen(right, bottom)
            rects.append((x1, y1, x2, y2))
        return rects

    def _layout(self, width: float, height: float) -> tuple[float, float, float, float]:
        scale = max(width / self.BACKGROUND_WIDTH, height / self.BACKGROUND_HEIGHT)
        shown_width = self.BACKGROUND_WIDTH * scale
        shown_height = self.BACKGROUND_HEIGHT * scale
        offset_x = (width - shown_width) / 2
        offset_y = (height - shown_height) / 2
        return offset_x, offset_y, shown_width, shown_height

    def _to_screen(self, fx: float, fy: float) -> tuple[float, float]:
        offset_x, offset_y, shown_width, shown_height = self._layout(self.width, self.height)
        return offset_x + fx * shown_width, offset_y + fy * shown_height

    def _to_fraction(
        self, sx: float, sy: float, width: float, height: float
    ) -> tuple[float, float]:
        offset_x, offset_y, shown_width, shown_height = self._layout(width, height)
        return (sx - offset_x) / shown_width, (sy - offset_y) / shown_height

    def _layers(self) -> list[ft.Control]:
        return [sprite.build() for sprite in self.sprites]