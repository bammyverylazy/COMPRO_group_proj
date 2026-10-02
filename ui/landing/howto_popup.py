from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import flet as ft

from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme


@dataclass(frozen=True)
class HowToSlide:
    image_path: str
    text: str


class HowToPopup(BaseWidget):
    WIDTH: int = Theme.CONTENT_WIDTH
    IMAGE_WIDTH: int = 240
    IMAGE_HEIGHT: int = 160
    CARD_COLOR: str = "#FFF8EC"
    BORDER_COLOR: str = "#6D4348"
    TITLE_COLOR: str = "#734547"
    BORDER_WIDTH: int = 3
    OVERLAY_COLOR: str = ft.Colors.with_opacity(0.6, ft.Colors.BLACK)
    
    def __init__(self, slides: list[HowToSlide], on_close: Callable[[], None]) -> None:
        super().__init__()
        self.slides = slides
        self.on_close = on_close
        self.current_index = 0
        self._image = ft.Image(
            src=self.slides[0].image_path,
            width=self.IMAGE_WIDTH,
            height=self.IMAGE_HEIGHT,
            fit=ft.BoxFit.COVER,
        )
        self._text = ft.Text(
            self.slides[0].text,
            size=Theme.BODY_SIZE,
            color=Theme.TEXT,
            text_align=ft.TextAlign.CENTER,
        )
        self._counter = ft.Text(f"1/{len(self.slides)}", color=Theme.MUTED)

    def build(self) -> ft.Control:
        image_frame = ft.Container(
            content=self._image,
            width=self.IMAGE_WIDTH,
            height=self.IMAGE_HEIGHT,
            alignment=ft.Alignment.CENTER,
            border_radius=8,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("HOW TO PLAY", size=Theme.HEADING_SIZE, weight=ft.FontWeight.BOLD, color=self.TITLE_COLOR),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_color=self.TITLE_COLOR, on_click=lambda _: self.on_close()),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                image_frame,
                self._text,
                ft.Row(
                    [
                        ft.TextButton("Previous", on_click=lambda _: self.prev()),
                        self._counter,
                        ft.TextButton("Next", on_click=lambda _: self.next()),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
            spacing=Theme.SPACING,
        )

    def as_overlay(self) -> ft.Container:
        card = ft.Container(
            content=self.control,
            width=self.WIDTH,
            bgcolor=self.CARD_COLOR,
            border=ft.Border.all(self.BORDER_WIDTH, self.BORDER_COLOR),
            border_radius=Theme.PANEL_RADIUS,
            padding=Theme.PANEL_PADDING,
            shadow=ft.BoxShadow(blur_radius=24, color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK)),
        )
        return ft.Container(
            content=card,
            bgcolor=self.OVERLAY_COLOR,
            alignment=ft.Alignment.CENTER,
            padding=Theme.PAGE_PADDING,
            expand=True,
        )

    def next(self) -> None:
        if self.current_index < len(self.slides) - 1:
            self.current_index += 1
            self._sync()

    def prev(self) -> None:
        if self.current_index > 0:
            self.current_index -= 1
            self._sync()

    def _sync(self) -> None:
        slide = self.slides[self.current_index]
        self._image.src = slide.image_path
        self._text.value = slide.text
        self._counter.value = f"{self.current_index + 1}/{len(self.slides)}"
        self.refresh()

    @staticmethod
    def default_slides() -> list[HowToSlide]:
        return [
            HowToSlide(
                image_path="howto/step1.png",
                text="Study for at least 15 minutes to earn an egg.",
            ),
            HowToSlide(
                image_path="howto/step2.png",
                text="The longer you study, the higher the chance to get higher tier eggs.",
            ),
            HowToSlide(
                image_path="howto/step3.png",
                text="Hatch eggs to collect rare characters in your CPE Dex.",
            ),
        ]
