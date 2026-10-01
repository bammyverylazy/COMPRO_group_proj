from __future__ import annotations

from typing import Callable, ClassVar

import flet as ft

from app.dto import DexEntry
from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme


class DexCard(BaseWidget):
    WIDTH: ClassVar[int] = 96
    HEIGHT: ClassVar[int] = 124
    IMAGE_SIZE: ClassVar[int] = 72
    LOCKED_NAME: ClassVar[str] = "???"
    LOCKED_BORDER: ClassVar[str] = "#55FFFFFF"
    CARD_COLOR: ClassVar[str] = "black54"
    SELECTED_WIDTH: ClassVar[int] = 3
    NORMAL_WIDTH: ClassVar[int] = 1

    def __init__(
        self,
        entry: DexEntry,
        on_select: Callable[[DexEntry], None],
        selected: bool = False,
    ) -> None:
        super().__init__()
        self.entry: DexEntry = entry
        self.on_select: Callable[[DexEntry], None] = on_select
        self.selected: bool = selected
        self._card: ft.Container | None = None

    def build(self) -> ft.Control:
        name = self.entry.species.name if self.entry.unlocked else self.LOCKED_NAME
        level_text = f"Lv.{self.entry.level}" if self.entry.unlocked else ""
        self._card = ft.Container(
            content=ft.Column(
                controls=[
                    self._image(),
                    ft.Text(
                        name,
                        size=12,
                        color=ft.Colors.WHITE,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(level_text, size=10, color=ft.Colors.WHITE),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                tight=True,
            ),
            width=self.WIDTH,
            height=self.HEIGHT,
            padding=6,
            bgcolor=self.CARD_COLOR,
            border_radius=12,
            border=self._border(),
            on_click=self._handle_click,
        )
        return self._card

    def set_selected(self, selected: bool) -> None:
        self.selected = selected
        if self._card is None:
            return
        self._card.border = self._border()
        self.refresh()

    def _image(self) -> ft.Control:
        if self.entry.unlocked:
            return ft.Image(
                src=self.entry.species.sprite_path,
                width=self.IMAGE_SIZE,
                height=self.IMAGE_SIZE,
                fit=ft.BoxFit.CONTAIN,
            )
        return ft.Image(
            src=self.entry.species.sprite_path,
            width=self.IMAGE_SIZE,
            height=self.IMAGE_SIZE,
            fit=ft.BoxFit.CONTAIN,
            color=ft.Colors.BLACK,
            color_blend_mode=ft.BlendMode.SRC_IN,
            opacity=0.7,
        )

    def _border(self) -> ft.Border:
        if self.selected:
            return ft.Border.all(self.SELECTED_WIDTH, Theme.ACCENT)
        if self.entry.unlocked:
            return ft.Border.all(self.NORMAL_WIDTH, Theme.rarity_color(self.entry.species.rarity))
        return ft.Border.all(self.NORMAL_WIDTH, self.LOCKED_BORDER)

    def _handle_click(self, event: ft.ControlEvent) -> None:
        self.on_select(self.entry)
