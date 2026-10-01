from __future__ import annotations

from typing import ClassVar

import flet as ft

from app.domain.enums import EggTier
from app.dto import PlayerDTO
from ui.core.base_widget import BaseWidget


class MemberList(BaseWidget):
    EGG_WIDTH: ClassVar[int] = 20
    EGG_HEIGHT: ClassVar[int] = 26
    FULL_OPACITY: ClassVar[float] = 1.0
    DIM_OPACITY: ClassVar[float] = 0.4
    GLOW_BASE: ClassVar[int] = 4
    GLOW_PER_PERCENT: ClassVar[float] = 0.5
    GLOW_COLOR: ClassVar[str] = ft.Colors.AMBER
    EGG_COLOR: ClassVar[str] = ft.Colors.AMBER_100

    def __init__(self, members: list[PlayerDTO]) -> None:
        super().__init__()
        self.members: list[PlayerDTO] = members
        self._eggs: list[ft.Container] = []

    def build(self) -> ft.Control:
        self._eggs = [self._build_egg() for _ in self.members]
        rows = [
            ft.Row([ft.Text(member.nickname, expand=True), egg])
            for member, egg in zip(self.members, self._eggs, strict=True)
        ]
        return ft.Column(rows)

    def set_egg_odds(self, odds: dict[EggTier, int]) -> None:
        is_reached = bool(odds)
        professor_percent = odds.get(EggTier.PROFESSOR, 0)
        glow = ft.BoxShadow(
            blur_radius=self.GLOW_BASE + professor_percent * self.GLOW_PER_PERCENT,
            color=self.GLOW_COLOR,
        )
        for egg in self._eggs:
            egg.opacity = self.FULL_OPACITY if is_reached else self.DIM_OPACITY
            egg.shadow = glow if is_reached else None
            egg.update()

    def _build_egg(self) -> ft.Container:
        return ft.Container(
            width=self.EGG_WIDTH,
            height=self.EGG_HEIGHT,
            border_radius=self.EGG_HEIGHT,
            bgcolor=self.EGG_COLOR,
            opacity=self.DIM_OPACITY,
        )