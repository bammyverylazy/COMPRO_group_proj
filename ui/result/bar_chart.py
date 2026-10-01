from __future__ import annotations

from typing import Callable, ClassVar

import flet as ft

from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme


class BarChart(BaseWidget):
    DEFAULT_BAR_HEIGHT: ClassVar[int] = 160
    BAR_WIDTH: ClassVar[int] = 34
    MIN_BAR: ClassVar[int] = 4
    GAP: ClassVar[int] = 6
    EMPTY_TEXT: ClassVar[str] = "No data"

    def __init__(
        self,
        values: dict[str, int],
        format_value: Callable[[int], str],
        bar_height: int = DEFAULT_BAR_HEIGHT,
    ) -> None:
        super().__init__()
        self.values: dict[str, int] = dict(values)
        self.format_value: Callable[[int], str] = format_value
        self.bar_height: int = bar_height

    def build(self) -> ft.Control:
        if not self.values:
            return ft.Container(content=ft.Text(self.EMPTY_TEXT, color=ft.Colors.WHITE), padding=8)

        max_value = max(max(self.values.values()), 1)
        bars: list[ft.Control] = [self._bar(label, value, max_value) for label, value in self.values.items()]

        return ft.Container(
            content=ft.Row(
                bars,
                spacing=self.GAP,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.END,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=8,
        )

    def _bar(self, label: str, value: int, max_value: int) -> ft.Control:
        height = max(self.MIN_BAR, int(value / max_value * self.bar_height))
        return ft.Column(
            [
                ft.Text(self.format_value(value) if value > 0 else "", size=9, color=ft.Colors.WHITE),
                ft.Container(
                    width=self.BAR_WIDTH,
                    height=height,
                    bgcolor=Theme.ACCENT if value > 0 else "white24",
                    border_radius=6,
                ),
                ft.Text(
                    label,
                    size=10,
                    color=ft.Colors.WHITE,
                    width=self.BAR_WIDTH + self.GAP,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        )
