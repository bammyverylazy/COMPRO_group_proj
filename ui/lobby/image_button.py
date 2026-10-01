from __future__ import annotations

from typing import Callable

import flet as ft

from ui.core.base_widget import BaseWidget


class ImageButton(BaseWidget):
    def __init__(
        self,
        normal_src: str,
        hover_src: str,
        on_click: Callable[[], None],
        height: float = 48,
    ) -> None:
        super().__init__()
        self.normal_src: str = normal_src
        self.hover_src: str = hover_src
        self.on_click: Callable[[], None] = on_click
        self.height: float = height
        self.image: ft.Image | None = None

    def build(self) -> ft.Control:
        self.image = ft.Image(
            src=self.normal_src,
            height=self.height,
            fit=ft.BoxFit.CONTAIN,
            gapless_playback=True,
        )
        return ft.Container(
            content=self.image,
            on_click=self._handle_click,
            on_hover=self._handle_hover,
        )

    def _handle_click(self, event: ft.ControlEvent) -> None:
        self.on_click()

    def _handle_hover(self, event: ft.ControlEvent) -> None:
        if self.image is None:
            return
        hovered: bool = event.data is True or event.data == "true"
        self.image.src = self.hover_src if hovered else self.normal_src
        self.image.update()
