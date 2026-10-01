from __future__ import annotations

from typing import ClassVar

import flet as ft

from app.domain.enums import EggTier
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.theme import Theme


class EggView(BaseWidget):
    GLOW_IMAGES: ClassVar[tuple[tuple[int, str], ...]] = (
        (0, "eggs/egg_glow_0.png"),
        (10, "eggs/egg_glow_1.png"),
        (25, "eggs/egg_glow_2.png"),
        (40, "eggs/egg_glow_3.png"),
    )
    TIER_ORDER: ClassVar[tuple[EggTier, ...]] = (
        EggTier.FRESHMAN,
        EggTier.SENIOR,
        EggTier.PROFESSOR,
    )
    TIER_COLORS: ClassVar[dict[EggTier, str]] = {
        EggTier.FRESHMAN: Theme.MUTED,
        EggTier.SENIOR: Theme.PRIMARY,
        EggTier.PROFESSOR: Theme.ACCENT,
    }
    EGG_SIZE: ClassVar[int] = 200
    BAR_HEIGHT: ClassVar[int] = 28
    BAR_WIDTH: ClassVar[int] = 280
    BAR_RADIUS: ClassVar[int] = 14
    BAR_TEXT_SIZE: ClassVar[int] = 12
    SPACING: ClassVar[int] = 12
    WOBBLE_SCALE: ClassVar[float] = 1.12
    NORMAL_SCALE: ClassVar[float] = 1.0
    WOBBLE_MS: ClassVar[int] = 250
    EMPTY_TEXT: ClassVar[str] = "Keep reading to earn an egg"

    def __init__(self, odds: dict[EggTier, int] | None = None) -> None:
        super().__init__()
        self.odds: dict[EggTier, int] = dict(odds) if odds else {}
        self.image: ft.Image | None = None
        self._frame: ft.Container | None = None
        self._bar: ft.Row | None = None
        self._wobbling: bool = False

    def build(self) -> ft.Control:
        self.image = ft.Image(src=self._image_path(), width=self.EGG_SIZE, height=self.EGG_SIZE)
        self._frame = ft.Container(
            content=self.image,
            scale=self.NORMAL_SCALE,
            animate_scale=ft.Animation(self.WOBBLE_MS, ft.AnimationCurve.EASE_OUT),
            on_animation_end=self._on_wobble_end,
        )
        self._bar = ft.Row(controls=self._bar_segments(), width=self.BAR_WIDTH, spacing=0)
        return ft.Column(
            controls=[self._frame, self._bar],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=self.SPACING,
            tight=True,
        )

    def set_odds(self, odds: dict[EggTier, int]) -> None:
        if odds == self.odds:
            return
        self.odds = dict(odds)
        if self.image is None or self._bar is None:
            return
        self.image.src = self._image_path()
        self._bar.controls = self._bar_segments()
        self.refresh()

    def wobble(self) -> None:
        if self._frame is None:
            return
        self._wobbling = True
        self._frame.scale = self.WOBBLE_SCALE
        self._frame.update()

    def _on_wobble_end(self, event: ft.ControlEvent) -> None:
        if self._frame is None or not self._wobbling:
            return
        self._wobbling = False
        self._frame.scale = self.NORMAL_SCALE
        self._frame.update()

    def _image_path(self) -> str:
        professor_percent: int = self.odds.get(EggTier.PROFESSOR, 0)
        path: str = self.GLOW_IMAGES[0][1]
        for threshold, glow_path in self.GLOW_IMAGES:
            if professor_percent >= threshold:
                path = glow_path
        return path

    def _bar_segments(self) -> list[ft.Control]:
        if not self.odds:
            return [ft.Text(self.EMPTY_TEXT, size=self.BAR_TEXT_SIZE, color=Theme.MUTED)]
        return [self._segment(tier) for tier in self.TIER_ORDER if self.odds.get(tier, 0) > 0]

    def _segment(self, tier: EggTier) -> ft.Control:
        percent: int = self.odds[tier]
        label: ft.Text = ft.Text(
            f"{Format.tier_name(tier)} {percent}%",
            size=self.BAR_TEXT_SIZE,
            color=Theme.BACKGROUND,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        return ft.Container(
            content=label,
            bgcolor=self.TIER_COLORS[tier],
            height=self.BAR_HEIGHT,
            border_radius=self.BAR_RADIUS,
            alignment=ft.Alignment(0, 0),
            expand=percent,
        )
