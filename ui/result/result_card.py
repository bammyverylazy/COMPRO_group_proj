from __future__ import annotations

import math
from typing import ClassVar

import flet as ft

from app.domain.enums import EggTier
from app.dto import SessionReport
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.theme import Theme


class ResultCard(BaseWidget):
    EGG_IMAGES: ClassVar[dict[EggTier, str]] = {
        EggTier.FRESHMAN: "eggs/freshman_egg.png",
        EggTier.SENIOR: "eggs/senior_egg.png",
        EggTier.PROFESSOR: "eggs/professor_egg.png",
    }
    FAILED_EGG: ClassVar[str] = "eggs/freshman_egg.png"
    SECONDS_PER_MINUTE: ClassVar[int] = 60
    SPRITE_SIZE: ClassVar[int] = 300
    EGG_SIZE: ClassVar[int] = 44
    TITLE_SIZE: ClassVar[int] = Theme.TITLE_SIZE
    CARD_PADDING: ClassVar[int] = Theme.PANEL_PADDING
    CARD_RADIUS: ClassVar[int] = Theme.PANEL_RADIUS
    CARD_COLOR: ClassVar[str] = Theme.PANEL_COLOR
    CARD_WIDTH: ClassVar[int] = 360

    def __init__(self, report: SessionReport, nickname: str) -> None:
        super().__init__()
        self.report: SessionReport = report
        self.nickname: str = nickname

    def build(self) -> ft.Control:
        body = self._build_success() if self.report.is_success else self._build_failed()
        controls: list[ft.Control] = [body]
        if self.report.room_id is not None:
            controls.insert(0, ft.Text(self.nickname, size=self.TITLE_SIZE, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE))

        return ft.Container(
            content=ft.Column(
                controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                tight=True,
            ),
            width=self.CARD_WIDTH,
            padding=self.CARD_PADDING,
            border_radius=self.CARD_RADIUS,
            bgcolor=self.CARD_COLOR,
        )

    def _build_success(self) -> ft.Control:
        pet = self.report.pet
        tier = self.report.tier
        controls: list[ft.Control] = [ft.Text(self.report.subject, color="white70")]
        if tier is not None:
            controls.append(
                ft.Row(
                    controls=[
                        ft.Image(src=self.EGG_IMAGES[tier], width=self.EGG_SIZE, height=self.EGG_SIZE, fit=ft.BoxFit.CONTAIN),
                        ft.Text(Format.tier_name(tier), color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
        if pet is not None:
            badge = "NEW!" if self.report.is_new else f"LEVEL UP! Lv.{pet.level}"
            sprite_size = int(self.SPRITE_SIZE * pet.scale)
            controls.extend(
                [
                    ft.Image(src=pet.species.sprite_path, width=sprite_size, height=sprite_size, fit=ft.BoxFit.CONTAIN),
                    ft.Text(pet.species.name, size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Text(pet.species.rarity.value.upper(), color=Theme.rarity_color(pet.species.rarity), weight=ft.FontWeight.BOLD),
                    ft.Text(badge, color=Theme.ACCENT, weight=ft.FontWeight.BOLD),
                ]
            )
        controls.append(ft.Text(f"Studied {Format.duration(self.report.duration_sec)}", color=ft.Colors.WHITE))
        return ft.Column(controls, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, tight=True)

    def _build_failed(self) -> ft.Control:
        remaining_minutes = math.ceil(self.report.remaining_sec / self.SECONDS_PER_MINUTE)
        return ft.Column(
            [
                ft.Text(self.report.subject, color="white70"),
                ft.Image(
                    src=self.FAILED_EGG,
                    width=self.EGG_SIZE,
                    height=self.EGG_SIZE,
                    fit=ft.BoxFit.CONTAIN,
                    color=ft.Colors.BLACK,
                    color_blend_mode=ft.BlendMode.SRC_IN,
                    opacity=0.5,
                ),
                ft.Text("No egg this time", size=Theme.HEADING_SIZE, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text(f"Studied {Format.duration(self.report.duration_sec)}", color=ft.Colors.WHITE),
                ft.Text(f"Study {remaining_minutes} more min to get an egg", color=Theme.ACCENT, weight=ft.FontWeight.BOLD),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            tight=True,
        )
