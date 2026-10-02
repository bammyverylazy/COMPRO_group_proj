from __future__ import annotations

import flet as ft

from ui.core.sound_manager import SoundManager


class VolumeControl:
    def __init__(self, sound: SoundManager) -> None:
        self.sound = sound

        self._bars: list[ft.Container] = []

        self.minus_button = ft.TextButton(
            content=ft.Text(
                "−",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            on_click=self._decrease,
        )

        self.plus_button = ft.TextButton(
            content=ft.Text(
                "+",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            on_click=self._increase,
        )

        for _ in range(10):
            self._bars.append(
                ft.Container(
                    width=8,
                    height=14,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=2,
                )
            )

        self.control = ft.Container(
            content=ft.Row(
                controls=[
                    self.minus_button,
                    ft.Row(
                        controls=self._bars,
                        spacing=2,
                        tight=True,
                    ),
                    self.plus_button,
                ],
                spacing=4,
                tight=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=4,
        )

    def _decrease(self, event: ft.ControlEvent) -> None:
        self.sound.decrease_volume()
        self._update_bars()

    def _increase(self, event: ft.ControlEvent) -> None:
        self.sound.increase_volume()
        self._update_bars()

    def _update_bars(self) -> None:
        level = self.sound.volume_level

        for index, bar in enumerate(self._bars):
            bar.bgcolor = (
                ft.Colors.WHITE
                if index < level
                else ft.Colors.with_opacity(
                    0.25,
                    ft.Colors.WHITE,
                )
            )

        self.control.update()