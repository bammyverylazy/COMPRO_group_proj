from __future__ import annotations
from typing import Callable
import flet as ft
from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme

_VARIANT_COLORS: dict[str, str] = {
    "primary": Theme.PRIMARY,
    "secondary": Theme.MUTED,
    "danger": Theme.ERROR,
}


class PixelButton(BaseWidget):
    def __init__(self,text: str,on_click: Callable[[], None],variant: str = "primary",disabled: bool = False,) -> None:
        super().__init__()
        self.text = text
        self.on_click = on_click
        self.variant = variant
        self.disabled = disabled

    def build(self) -> ft.Control:
        return ft.ElevatedButton(
            text=self.text,
            disabled=self.disabled,
            bgcolor=_VARIANT_COLORS.get(self.variant, Theme.PRIMARY),
            color=ft.Colors.WHITE,
            on_click=lambda _: self.on_click(),
        )

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
            border_radius=16,
            padding=20,
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
    ) -> None:
        self.title = title
        self.on_yes = on_yes
        self.on_no = on_no
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
                ft.TextButton("NO", on_click=handle_no),
                ft.TextButton("YES", on_click=handle_yes),
            ],
        )
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
            border_radius=12,
            padding=16,
            content=ft.Column(
                [
                    ft.Text(self.value, size=24, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                    ft.Text(self.label, size=12, color=Theme.MUTED),
                ]
            ),
        )

