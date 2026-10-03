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

    # อัตรา tick ขั้นต่ำ: ยิ่งถี่ ก้าวของตัวละครยิ่งเล็ก (30 fps ที่ speed 40 = ราว 1.3 px ต่อก้าว)
    MIN_FPS: int = 30

    # ตัวละครต้องแซงกันเกินระยะนี้ (px) ถึงจะสลับลำดับชั้นการวาด
    REORDER_MARGIN: float = 8.0

    # ตรวจและสลับลำดับชั้นการวาดไม่เกินทุก ๆ กี่วินาที
    # (การแทนที่ stack.controls อาจทำให้ widget ถูกสร้างใหม่ จึงไม่ทำถี่)
    REORDER_INTERVAL: float = 0.5

    # ปิดเป็น False เพื่อทดสอบว่าการสลับลำดับเป็นต้นเหตุของการกระโดดหรือไม่
    ENABLE_REORDER: bool = True

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
        return self.stack

    def resize(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
        area = self._area()
        obstacles = self._obstacles()
        for sprite in self.sprites:
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

        # เรียงลำดับเริ่มต้นตามเท้าครั้งเดียว
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
        # กำหนดเวลา tick แบบไม่สะสมความคลาดเคลื่อน
        # (ถ้า tick ใช้เวลานาน รอบถัดไปจะชดเชยโดยไม่ sleep เพิ่ม)
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
                # ช้ากว่ากำหนด: ไม่ไล่ชดเชยหลายรอบติดกัน
                next_at = time.perf_counter()
                delay = 0.0
            await asyncio.sleep(delay)

    def tick(self, dt: float | None = None) -> None:
        """dt ไม่ได้ใช้แล้ว (เก็บพารามิเตอร์ไว้เพื่อให้โค้ดเดิมที่เรียก tick(dt) ยังทำงานได้)"""
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
        """Insertion sort แบบมี margin คืน True ถ้าลำดับเปลี่ยน"""
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

    def _to_screen(self, fx: float, fy: float) -> tuple[float, float]:
        scale = max(self.width / self.BACKGROUND_WIDTH, self.height / self.BACKGROUND_HEIGHT)
        shown_width = self.BACKGROUND_WIDTH * scale
        shown_height = self.BACKGROUND_HEIGHT * scale
        offset_x = (self.width - shown_width) / 2
        offset_y = (self.height - shown_height) / 2
        return offset_x + fx * shown_width, offset_y + fy * shown_height

    def _layers(self) -> list[ft.Control]:
        return [sprite.build() for sprite in self.sprites]