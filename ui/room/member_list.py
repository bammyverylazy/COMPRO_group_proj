from __future__ import annotations

from typing import ClassVar

import flet as ft

from app.domain.enums import EggTier
from app.dto import PlayerDTO
from ui.core.base_widget import BaseWidget


class MemberList(BaseWidget):
    EGG_IMAGES: ClassVar[tuple[tuple[int, str], ...]] = (
        (0, "eggs/freshman_egg.png"),
        (10, "eggs/senior_egg.png"),
        (40, "eggs/professor_egg.png"),
    )
    EGG_SIZE: ClassVar[int] = 40
    ITEM_WIDTH: ClassVar[int] = 72

    def __init__(self, members: list[PlayerDTO]) -> None:
        super().__init__()
        self.members: list[PlayerDTO] = list(members)
        self.odds: dict[EggTier, int] = {}
        self._images: list[ft.Image] = []

    def build(self) -> ft.Control:
        self._images = []
        items: list[ft.Control] = []
        for member in self.members:
            image = ft.Image(
                src=self._egg_path(),
                width=self.EGG_SIZE,
                height=self.EGG_SIZE,
                fit=ft.BoxFit.CONTAIN,
                opacity=self._egg_opacity(),
            )
            self._images.append(image)
            items.append(
                ft.Column(
                    controls=[
                        image,
                        ft.Text(
                            member.nickname,
                            size=12,
                            color=ft.Colors.WHITE,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                    width=self.ITEM_WIDTH,
                    tight=True,
                )
            )
        return ft.Row(controls=items, wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=8, run_spacing=8)

    def set_egg_odds(self, odds: dict[EggTier, int]) -> None:
        if odds == self.odds:
            return
        self.odds = dict(odds)
        for image in self._images:
            image.src = self._egg_path()
            image.opacity = self._egg_opacity()
        self.refresh()

    def _egg_path(self) -> str:
        professor_percent = self.odds.get(EggTier.PROFESSOR, 0)
        path = self.EGG_IMAGES[0][1]
        for threshold, egg_path in self.EGG_IMAGES:
            if professor_percent >= threshold:
                path = egg_path
        return path

    def _egg_opacity(self) -> float:
        return 1.0 if self.odds else 0.4
