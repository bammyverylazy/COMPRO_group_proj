from __future__ import annotations

from typing import Callable, ClassVar

import flet as ft

from ui.core.base_widget import BaseWidget


class BarChart(BaseWidget):
    DEFAULT_BAR_HEIGHT: ClassVar[int] = 160
    BAR_WIDTH: ClassVar[int] = 28
    GAP: ClassVar[int] = 8

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
            return ft.Container(content=ft.Text("No data"), padding=8)

        max_value = max(self.values.values())
        if max_value <= 0:
            max_value = 1

        bars: list[ft.Control] = []
        for label, value in self.values.items():
            height = max(8, int((value / max_value) * self.bar_height))
            bars.append(
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(self.format_value(value), size=10, color=ft.Colors.WHITE),
                            width=self.BAR_WIDTH,
                            height=height,
                            bgcolor=ft.Colors.BLUE_400,
                            border_radius=8,
                            alignment=ft.alignment.center,
                        ),
                        ft.Text(label, size=10),
                    ],
                    spacing=4,
                    alignment=ft.MainAxisAlignment.END,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        return ft.Container(
            content=ft.Row(
                bars,
                spacing=self.GAP,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            padding=8,
        )
