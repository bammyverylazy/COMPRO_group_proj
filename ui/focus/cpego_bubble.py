from __future__ import annotations

import asyncio
from typing import ClassVar

import flet as ft

from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme
from ui.focus.cpego_bot import CpegoMessage


class CpegoBubble(BaseWidget):
    IMAGE_PATH: ClassVar[str] = "cpego/cpego.png"
    IMAGE_SIZE: ClassVar[int] = 72
    MAX_TEXT_WIDTH: ClassVar[int] = 240
    TEXT_SIZE: ClassVar[int] = 14
    PADDING: ClassVar[int] = 12
    RADIUS: ClassVar[int] = 12
    SPACING: ClassVar[int] = 8
    POP_SCALE: ClassVar[float] = 0.8
    NORMAL_SCALE: ClassVar[float] = 1.0
    POP_DELAY_SEC: ClassVar[float] = 0.05
    ANIMATION_MS: ClassVar[int] = 200

    def __init__(self, show_sec: float = 5.0) -> None:
        super().__init__()
        self.show_sec: float = show_sec
        self.visible: bool = False
        self.text: ft.Text | None = None
        self._hide_token: int = 0

    def build(self) -> ft.Control:
        self.text = ft.Text(
            "",
            size=self.TEXT_SIZE,
            color=Theme.TEXT,
            width=self.MAX_TEXT_WIDTH,
        )
        message_box: ft.Container = ft.Container(
            content=self.text,
            bgcolor=Theme.BACKGROUND,
            border_radius=self.RADIUS,
            padding=self.PADDING,
        )
        image: ft.Image = ft.Image(src=self.IMAGE_PATH, width=self.IMAGE_SIZE, height=self.IMAGE_SIZE)
        return ft.Container(
            content=ft.Row(controls=[image, message_box], spacing=self.SPACING),
            visible=self.visible,
            scale=self.NORMAL_SCALE,
            animate_scale=ft.Animation(self.ANIMATION_MS, ft.AnimationCurve.EASE_OUT),
        )

    def show(self, page: ft.Page, message: CpegoMessage) -> None:
        control: ft.Control = self.control
        if self.text is None:
            return
        self._hide_token += 1
        self.text.value = message.text
        self.visible = True
        control.visible = True
        control.scale = self.POP_SCALE
        control.update()
        page.run_task(self._run, self._hide_token)

    def hide(self) -> None:
        self.visible = False
        if self._control is None:
            return
        self._control.visible = False
        self.refresh()

    async def _run(self, token: int) -> None:
        await asyncio.sleep(self.POP_DELAY_SEC)
        if self._control is not None and token == self._hide_token:
            self._control.scale = self.NORMAL_SCALE
            self.refresh()
        await asyncio.sleep(self.show_sec)
        if token == self._hide_token:
            self.hide()
