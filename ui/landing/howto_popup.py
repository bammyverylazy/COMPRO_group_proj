from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import flet as ft

from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme
from ui.core.widgets import PixelButton


@dataclass(frozen=True)
class HowToSlide:
    image_path: str
    text: str


class HowToPopup(BaseWidget):
    WIDTH: int = Theme.CONTENT_WIDTH - 100

    def __init__(self, slides: list[HowToSlide], on_close: Callable[[], None]) -> None:
        super().__init__()
        self.slides = slides
        self.on_close = on_close
        self.current_index = 0
        self._image = ft.Image(src=self.slides[0].image_path, height=160)
        self._text = ft.Text(
            self.slides[0].text,
            size=14,
            color=Theme.TEXT,
            text_align=ft.TextAlign.CENTER,
        )
        self._counter = ft.Text(f"1/{len(self.slides)}", color=Theme.MUTED)

    def build(self) -> ft.Control:
        return ft.Container(
            bgcolor=Theme.BACKGROUND,
            border_radius=16,
            padding=Theme.PANEL_PADDING,
            width=self.WIDTH,
            content=ft.Column(
                [
                    ft.Row(
                        [ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda _: self.on_close())],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    self._image,
                    self._text,
                    ft.Row(
                        [
                            ft.TextButton("Previous", on_click=lambda _: self.prev()),
                            self._counter,
                            ft.TextButton("Next", on_click=lambda _: self.next()),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    PixelButton("BACK", self.on_close, variant="secondary").control,
                ],
                tight=True,
                spacing=Theme.SPACING,
            ),
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
                image_path="eggs/freshman.png",
                text="Study for at least 15 minutes to earn an egg.",
            ),
            HowToSlide(
                image_path="eggs/senior.png",
                text="The longer you study, the higher the chance to get higher tier eggs.",
            ),
            HowToSlide(
                image_path="eggs/professor.png",
                text="Hatch eggs to collect rare characters in your CPE Dex.",
            ),
        ]

