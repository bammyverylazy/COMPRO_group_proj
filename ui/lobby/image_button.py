from __future__ import annotations

from typing import Callable

import flet as ft

from ui.core.base_widget import BaseWidget
from ui.lobby.pet_sprite import asset_exists


class ImageButton(BaseWidget):
    def __init__(
        self,
        normal_src: str,
        hover_src: str,
        on_click: Callable[[], None],
        height: float = 48,
        label: str = "",
    ) -> None:
        super().__init__()
        self.normal_src: str = self._resolve_asset(normal_src)
        self.hover_src: str = self._resolve_asset(hover_src)
        self.on_click: Callable[[], None] = on_click
        self.height: float = height
        self.label: str = label
        self.image: ft.Image | None = None

    def build(self) -> ft.Control:
        if not self.normal_src:
            return ft.FilledButton(content=ft.Text(self.label or "BUTTON"), on_click=self._handle_click, height=self.height)
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

    def _resolve_asset(self, path: str) -> str:
        if asset_exists(path):
            return path
        return path  

    def _handle_click(self, event: ft.ControlEvent) -> None:
        self.on_click()

    def _handle_hover(self, event: ft.ControlEvent) -> None:
        if self.image is None or not self.hover_src:
            return
        hovered: bool = event.data is True or event.data == "true"
        self.image.src = self.hover_src if hovered else self.normal_src
        self.image.update()