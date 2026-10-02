from __future__ import annotations

import asyncio
from typing import Callable, ClassVar

import flet as ft

from app.domain.enums import EggTier
from app.dto import PetDTO
from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme


class HatchAnimation(BaseWidget):
    STAGES: ClassVar[tuple[str, ...]] = ("roulette", "shake", "crack", "reveal")
    EGG_IMAGES: ClassVar[dict[EggTier, str]] = {
        EggTier.FRESHMAN: "eggs/freshman_egg.png",
        EggTier.SENIOR: "eggs/senior_egg.png",
        EggTier.PROFESSOR: "eggs/professor_egg.png",
    }
    TIER_ORDER: ClassVar[tuple[EggTier, ...]] = (
        EggTier.FRESHMAN,
        EggTier.SENIOR,
        EggTier.PROFESSOR,
    )
    AREA_SIZE: ClassVar[int] = 260
    EGG_SIZE: ClassVar[int] = 180
    PET_SIZE: ClassVar[int] = 220
    ROULETTE_STEPS: ClassVar[int] = 12
    ROULETTE_START_SEC: ClassVar[float] = 0.06
    ROULETTE_GROWTH_SEC: ClassVar[float] = 0.02
    SHAKE_TIMES: ClassVar[int] = 8
    SHAKE_ANGLE: ClassVar[float] = 0.18
    SHAKE_MS: ClassVar[int] = 70
    TADA_TEXT: ClassVar[str] = "TADA!"

    def __init__(self, tier: EggTier, pet: PetDTO, stage_ms: int = 900) -> None:
        super().__init__()
        self.tier: EggTier = tier
        self.pet: PetDTO = pet
        self.stage_ms: int = stage_ms
        self.current_stage: int = 0
        self.stack: ft.Stack | None = None
        self._egg_image: ft.Image | None = None
        self._egg: ft.Container | None = None
        self._flash: ft.Container | None = None
        self._pet: ft.Container | None = None
        self._tada: ft.Text | None = None
        self._on_done: Callable[[], None] | None = None
        self._finished: bool = False

    def build(self) -> ft.Control:
        self._egg_image = ft.Image(
            src=self.EGG_IMAGES[self.TIER_ORDER[0]],
            width=self.EGG_SIZE,
            height=self.EGG_SIZE,
            fit=ft.BoxFit.CONTAIN,
            gapless_playback=True,
        )
        self._egg = ft.Container(
            content=self._egg_image,
            alignment=ft.Alignment.CENTER,
            rotate=0.0,
            scale=1.0,
            opacity=1.0,
            animate_rotation=ft.Animation(self.SHAKE_MS, ft.AnimationCurve.EASE_IN_OUT),
            animate_scale=ft.Animation(self._stage_ms_part(3), ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.Animation(self._stage_ms_part(3), ft.AnimationCurve.EASE_OUT),
        )
        self._flash = ft.Container(
            width=self.AREA_SIZE,
            height=self.AREA_SIZE,
            bgcolor=ft.Colors.WHITE,
            border_radius=self.AREA_SIZE,
            opacity=0.0,
            animate_opacity=ft.Animation(self._stage_ms_part(3), ft.AnimationCurve.EASE_OUT),
        )
        self._pet = ft.Container(
            content=ft.Image(
                src=self.pet.species.sprite_path,
                width=self.PET_SIZE,
                height=self.PET_SIZE,
                fit=ft.BoxFit.CONTAIN,
            ),
            alignment=ft.Alignment.CENTER,
            scale=0.0,
            opacity=0.0,
            animate_scale=ft.Animation(self.stage_ms, ft.AnimationCurve.ELASTIC_OUT),
            animate_opacity=ft.Animation(self._stage_ms_part(3), ft.AnimationCurve.EASE_OUT),
        )
        self._tada = ft.Text(
            self.TADA_TEXT,
            size=32,
            weight=ft.FontWeight.BOLD,
            color=Theme.ACCENT,
            opacity=0.0,
            animate_opacity=ft.Animation(self._stage_ms_part(2), ft.AnimationCurve.EASE_OUT),
        )
        self.stack = ft.Stack(
            controls=[
                ft.Container(content=self._flash, alignment=ft.Alignment.CENTER, left=0, right=0, top=0, bottom=0),
                ft.Container(content=self._egg, alignment=ft.Alignment.CENTER, left=0, right=0, top=0, bottom=0),
                ft.Container(content=self._pet, alignment=ft.Alignment.CENTER, left=0, right=0, top=0, bottom=0),
                ft.Container(content=self._tada, alignment=ft.Alignment.TOP_CENTER, left=0, right=0, top=0),
            ],
            width=self.AREA_SIZE,
            height=self.AREA_SIZE,
        )
        return self.stack

    def play(self, page: ft.Page, on_done: Callable[[], None]) -> None:
        self._on_done = on_done
        self._finished = False
        self.current_stage = 0
        page.run_task(self._run)

    def skip(self) -> None:
        if self._finished:
            return
        self.current_stage = len(self.STAGES) - 1
        self._show_final()
        self._finish()

    async def _run(self) -> None:
        await self._roulette()
        if self._finished:
            return
        self.current_stage = 1
        await self._shake()
        if self._finished:
            return
        self.current_stage = 2
        await self._crack()
        if self._finished:
            return
        self.current_stage = 3
        self._show_final()
        await asyncio.sleep(self.stage_ms / 1000)
        self._finish()

    async def _roulette(self) -> None:
        if self._egg_image is None:
            return
        target_index = self.TIER_ORDER.index(self.tier)
        total_steps = self.ROULETTE_STEPS + target_index
        for step in range(total_steps + 1):
            if self._finished:
                return
            self._egg_image.src = self.EGG_IMAGES[self.TIER_ORDER[step % len(self.TIER_ORDER)]]
            self._update()
            await asyncio.sleep(self.ROULETTE_START_SEC + step * self.ROULETTE_GROWTH_SEC)
        self._egg_image.src = self.EGG_IMAGES[self.tier]
        self._update()
        await asyncio.sleep(self.stage_ms / 2000)

    async def _shake(self) -> None:
        if self._egg is None:
            return
        for index in range(self.SHAKE_TIMES):
            if self._finished:
                return
            self._egg.rotate = self.SHAKE_ANGLE if index % 2 == 0 else -self.SHAKE_ANGLE
            self._update()
            await asyncio.sleep(self.SHAKE_MS / 1000)
        self._egg.rotate = 0.0
        self._update()

    async def _crack(self) -> None:
        if self._egg is None or self._flash is None:
            return
        self._egg.scale = 1.3
        self._egg.opacity = 0.0
        self._flash.opacity = 0.9
        self._update()
        await asyncio.sleep(self._stage_ms_part(3) / 1000)
        self._flash.opacity = 0.0
        self._update()

    def _show_final(self) -> None:
        if self._egg is None or self._pet is None or self._tada is None or self._flash is None:
            return
        self._egg.opacity = 0.0
        self._egg.rotate = 0.0
        self._flash.opacity = 0.0
        self._pet.scale = 1.0
        self._pet.opacity = 1.0
        self._tada.opacity = 1.0
        self._update()

    def _finish(self) -> None:
        if self._finished:
            return
        self._finished = True
        if self._on_done is not None:
            self._on_done()

    def _stage_ms_part(self, parts: int) -> int:
        return max(1, self.stage_ms // parts)

    def _update(self) -> None:
        if self.stack is None:
            return
        try:
            self.stack.update()
        except RuntimeError:
            return
