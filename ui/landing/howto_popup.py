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
    def __init__(self, slides: list[HowToSlide], on_close: Callable[[], None]) -> None:
        super().__init__()
        self.slides = slides
        self.on_close = on_close
        self.current_index = 0
        self._image = ft.Image(src=self.slides[0].image_path, height=200)
        self._text = ft.Text(
            self.slides[0].text,
            size=16,
            color=Theme.TEXT,
            text_align=ft.TextAlign.CENTER,
        )
        self._counter = ft.Text(f"1/{len(self.slides)}", color=Theme.MUTED)

    def build(self) -> ft.Control:
        return ft.Container(
            bgcolor=Theme.BACKGROUND,
            border_radius=16,
            padding=20,
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
                            ft.TextButton("ก่อนหน้า", on_click=lambda _: self.prev()),
                            self._counter,
                            ft.TextButton("ถัดไป", on_click=lambda _: self.next()),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ]
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
                text="อ่านหนังสือให้ครบ 15 นาทีขึ้นไปเพื่อลุ้นไข่",
            ),
            HowToSlide(
                image_path="eggs/senior.png",
                text="ยิ่งอ่านนาน โอกาสได้ไข่ระดับสูงยิ่งมากขึ้น",
            ),
            HowToSlide(
                image_path="eggs/professor.png",
                text="ฟักไข่เพื่อลุ้นตัวละครหายาก แล้วเก็บสะสมใน CPE Dex",
            ),
        ]

