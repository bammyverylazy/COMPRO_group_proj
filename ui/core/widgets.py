from __future__ import annotations
from typing import Callable
import flet as ft

from ui.core.base_widget import BaseWidget
from ui.core.sound_manager import SoundManager
from ui.core.theme import Theme

_VARIANT_COLORS: dict[str, str] = {
    "primary": Theme.PRIMARY,
    "secondary": Theme.MUTED,
    "danger": Theme.ERROR,
}


class PixelButton(BaseWidget):
    BORDER_WIDTH: int = 2
    CORNER_RADIUS: int = 6

    def __init__(
        self,
        text: str,
        on_click: Callable[[], None],
        variant: str = "primary",
        disabled: bool = False,
        sound: SoundManager | None = None,
    ) -> None:
        super().__init__()
        self.text = text
        self.on_click = on_click
        self.variant = variant
        self.disabled = disabled
        self.sound = sound

    def build(self) -> ft.Control:
        color = _VARIANT_COLORS.get(self.variant, Theme.PRIMARY)
        button = ft.FilledButton(
            content=ft.Text(
                self.text.upper(),
                color=ft.Colors.WHITE,
                size=Theme.BODY_SIZE,
                weight=ft.FontWeight.BOLD,
            ),
            height=Theme.IMAGE_BUTTON_HEIGHT,
            disabled=self.disabled,
            style=ft.ButtonStyle(
                bgcolor=color,
                shape=ft.RoundedRectangleBorder(radius=self.CORNER_RADIUS),
                side=ft.BorderSide(self.BORDER_WIDTH, ft.Colors.with_opacity(0.6, ft.Colors.BLACK)),
                padding=ft.Padding.symmetric(horizontal=Theme.SPACING, vertical=0),
            ),
            on_click=lambda _: self.on_click(),
        )
        if self.sound is not None:
            self.sound.bind_button(button)
        return button

    def set_disabled(self, disabled: bool) -> None:
        self.disabled = disabled
        self.control.disabled = disabled
        self.refresh()


class Popup(BaseWidget):
    def __init__(
        self,
        title: str,
        content: ft.Control,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.title = title
        self.content = content
        self.on_close = on_close
        self.is_open = False

    def build(self) -> ft.Control:
        header_controls: list[ft.Control] = [
            ft.Text(self.title, size=20, weight=ft.FontWeight.BOLD, color=Theme.TEXT)
        ]
        if self.on_close is not None:
            header_controls.append(
                ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda _: self.on_close())
            )
        return ft.Container(
            bgcolor=Theme.BACKGROUND,
            border_radius=Theme.PANEL_RADIUS,
            padding=Theme.PANEL_PADDING,
            content=ft.Column(
                [
                    ft.Row(header_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    self.content,
                ]
            ),
        )

    def open(self, page: ft.Page) -> None:
        self.is_open = True
        page.overlay.append(self.control)
        page.update()

    def close(self, page: ft.Page) -> None:
        self.is_open = False
        if self.control in page.overlay:
            page.overlay.remove(self.control)
        page.update()


class ConfirmDialog:
    def __init__(
        self,
        title: str,
        on_yes: Callable[[], None],
        on_no: Callable[[], None] | None = None,
        sound: SoundManager | None = None,
    ) -> None:
        self.title = title
        self.on_yes = on_yes
        self.on_no = on_no
        self.sound = sound
        self._dialog: ft.AlertDialog | None = None

    def open(self, page: ft.Page) -> None:
        def handle_yes(_: ft.ControlEvent) -> None:
            self.close(page)
            self.on_yes()

        def handle_no(_: ft.ControlEvent) -> None:
            self.close(page)
            if self.on_no is not None:
                self.on_no()

        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(self.title),
            actions=[
                ft.TextButton(content=ft.Text("NO"), on_click=handle_no),
                ft.TextButton(content=ft.Text("YES"), on_click=handle_yes),
            ],
        )
        if self.sound is not None:
            for button in self._dialog.actions:
                self.sound.bind_button(button)
        page.overlay.append(self._dialog)
        self._dialog.open = True
        page.update()

    def close(self, page: ft.Page) -> None:
        if self._dialog is not None:
            self._dialog.open = False
            page.update()


class StatTile(BaseWidget):
    def __init__(self, label: str, value: str) -> None:
        super().__init__()
        self.label = label
        self.value = value

    def build(self) -> ft.Control:
        return ft.Container(
            bgcolor=Theme.BACKGROUND,
            border_radius=Theme.PANEL_RADIUS,
            padding=Theme.PANEL_PADDING,
            content=ft.Column(
                [
                    ft.Text(self.value, size=Theme.HEADING_SIZE, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                    ft.Text(self.label, size=Theme.SMALL_SIZE, color=Theme.MUTED),
                ]
            ),
        )
