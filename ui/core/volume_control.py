from __future__ import annotations

import flet as ft

from ui.core.sound_manager import SoundManager


class VolumeControl:
    def __init__(self, sound: SoundManager) -> None:
        self.sound = sound
        self.expanded = False

        self.icon_button = ft.IconButton(
            icon=self._get_icon(),
            icon_color=ft.Colors.WHITE,
            icon_size=22,
            tooltip="Volume",
            on_click=self._toggle,
        )
        self.sound.bind_button(self.icon_button)

        self.slider = ft.Slider(
            min=0,
            max=10,
            divisions=10,
            value=self.sound.volume_level,
            width=100,
            active_color=ft.Colors.WHITE,
            inactive_color=ft.Colors.with_opacity(
                0.3,
                ft.Colors.WHITE,
            ),
            thumb_color=ft.Colors.WHITE,
            on_change=self._change_volume,
        )

        self.slider.visible = False

        self.control = ft.Row(
            controls=[
                self.icon_button,
                self.slider,
            ],
            spacing=2,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _toggle(self, event: ft.ControlEvent) -> None:
        self.expanded = not self.expanded
        self.slider.visible = self.expanded
        self.control.update()

    def _change_volume(self, event: ft.ControlEvent) -> None:
        level = int(event.control.value)

        while self.sound.volume_level < level:
            self.sound.increase_volume()

        while self.sound.volume_level > level:
            self.sound.decrease_volume()

        self.icon_button.icon = self._get_icon()
        self.icon_button.update()

    def _get_icon(self) -> str:
        if self.sound.volume_level == 0:
            return ft.Icons.VOLUME_OFF

        if self.sound.volume_level <= 3:
            return ft.Icons.VOLUME_DOWN

        return ft.Icons.VOLUME_UP