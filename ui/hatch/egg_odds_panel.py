from __future__ import annotations

from typing import ClassVar

import flet as ft

from app.domain.enums import EggTier
from app.dto import TierOdds
from app.errors import ValidationError
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.theme import Theme


class EggOddsPanel(BaseWidget):
    TIER_ORDER: ClassVar[tuple[EggTier, ...]] = (
        EggTier.FRESHMAN,
        EggTier.SENIOR,
        EggTier.PROFESSOR,
    )
    SECONDS_PER_MINUTE: ClassVar[int] = 60
    LABEL_FLEX: ClassVar[int] = 3
    CELL_FLEX: ClassVar[int] = 2
    FONT_SIZE: ClassVar[int] = Theme.BODY_SIZE
    ROW_PADDING: ClassVar[int] = 8
    ROW_SPACING: ClassVar[int] = 2
    RADIUS: ClassVar[int] = 6
    HIGHLIGHT_OPACITY: ClassVar[float] = 0.18
    HEADER_LABEL: ClassVar[str] = "Study time"
    NO_EGG_TEXT: ClassVar[str] = "No egg"

    def __init__(self, brackets: list[TierOdds], current_sec: int = 0, text_color: str = Theme.TEXT) -> None:
        super().__init__()
        if not brackets:
            raise ValidationError("No egg odds table", field="brackets")
        self.brackets: list[TierOdds] = brackets
        self.current_sec: int = current_sec
        self.text_color: str = text_color
        self._rows: list[ft.Container] = []

    def build(self) -> ft.Control:
        tier_names: list[str] = [Format.tier_name(tier) for tier in self.TIER_ORDER]
        header: ft.Container = self._build_row(self.HEADER_LABEL, tier_names, bold=True)
        self._rows = [self._build_under_row()]
        self._rows.extend(self._build_bracket_row(bracket) for bracket in self.brackets)
        self._apply_highlight()
        return ft.Column(controls=[header, *self._rows], spacing=self.ROW_SPACING, tight=True)

    def set_current(self, duration_sec: int) -> None:
        changed: bool = self._highlight_index(duration_sec) != self._highlight_index(self.current_sec)
        self.current_sec = duration_sec
        if not changed or self._control is None:
            return
        self._apply_highlight()
        self.refresh()

    def _build_under_row(self) -> ft.Container:
        label: str = f"Under {self.brackets[0].min_minutes} min"
        cells: list[str] = [self.NO_EGG_TEXT, "", ""]
        return self._build_row(label, cells)

    def _build_bracket_row(self, bracket: TierOdds) -> ft.Container:
        cells: list[str] = [f"{bracket.weights.get(tier, 0)}%" for tier in self.TIER_ORDER]
        return self._build_row(self._bracket_label(bracket), cells)

    def _bracket_label(self, bracket: TierOdds) -> str:
        if bracket.max_minutes is None:
            return f"{bracket.min_minutes}+ min"
        return f"{bracket.min_minutes}–{bracket.max_minutes} min"

    def _build_row(self, label: str, cells: list[str], bold: bool = False) -> ft.Container:
        weight: ft.FontWeight = ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL
        controls: list[ft.Control] = [
            ft.Text(label, size=self.FONT_SIZE, weight=weight, color=self.text_color, expand=self.LABEL_FLEX)
        ]
        controls.extend(self._build_cell(cell, weight) for cell in cells)
        return ft.Container(
            content=ft.Row(controls=controls),
            padding=self.ROW_PADDING,
            border_radius=self.RADIUS,
        )

    def _build_cell(self, text: str, weight: ft.FontWeight) -> ft.Control:
        return ft.Text(
            text,
            size=self.FONT_SIZE,
            weight=weight,
            color=self.text_color,
            text_align=ft.TextAlign.CENTER,
            expand=self.CELL_FLEX,
        )

    def _highlight_index(self, duration_sec: int) -> int | None:
        if duration_sec <= 0:
            return None
        matched: int = 0
        for index, bracket in enumerate(self.brackets, start=1):
            if duration_sec >= bracket.min_minutes * self.SECONDS_PER_MINUTE:
                matched = index
        return matched

    def _apply_highlight(self) -> None:
        active: int | None = self._highlight_index(self.current_sec)
        color: str = ft.Colors.with_opacity(self.HIGHLIGHT_OPACITY, Theme.ACCENT)
        for index, row in enumerate(self._rows):
            row.bgcolor = color if index == active else None
