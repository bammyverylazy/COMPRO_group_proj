from __future__ import annotations

import math
from typing import ClassVar

import flet as ft

from app.domain.enums import EggTier
from app.dto import SessionReport
from ui.core.base_widget import BaseWidget
from ui.core.format import Format


class ResultCard(BaseWidget):
    TIER_NAMES: ClassVar[dict[EggTier, str]] = {
        EggTier.FRESHMAN: "ไข่รุ่นเรา",
        EggTier.SENIOR: "ไข่รุ่นพี่",
        EggTier.PROFESSOR: "ไข่อาจารย์",
    }
    SECONDS_PER_MINUTE: ClassVar[int] = 60
    SPRITE_SIZE: ClassVar[int] = 96
    TITLE_SIZE: ClassVar[int] = 20
    CARD_PADDING: ClassVar[int] = 16
    CARD_RADIUS: ClassVar[int] = 12
    CARD_COLOR: ClassVar[str] = ft.Colors.BLUE_GREY_900

    def __init__(self, report: SessionReport, nickname: str) -> None:
        super().__init__()
        self.report: SessionReport = report
        self.nickname: str = nickname

    def build(self) -> ft.Control:
        body = self._build_success() if self.report.is_success else self._build_failed()
        controls = [body]
        if self.report.room_id is not None:
            controls.insert(0, ft.Text(self.nickname, size=self.TITLE_SIZE))
        return ft.Container(
            content=ft.Column(
                controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=self.CARD_PADDING,
            border_radius=self.CARD_RADIUS,
            bgcolor=self.CARD_COLOR,
        )

    def _build_success(self) -> ft.Control:
        pet = self.report.pet
        sprite_size = int(self.SPRITE_SIZE * pet.scale)
        badge = "ตัวใหม่!" if self.report.is_new else f"LEVEL UP! Lv.{pet.level}"
        return ft.Column(
            [
                ft.Text(self.report.subject),
                ft.Text(self.TIER_NAMES[self.report.tier]),
                ft.Image(src=pet.species.sprite_path, width=sprite_size, height=sprite_size),
                ft.Text(pet.species.name),
                ft.Text(badge, weight=ft.FontWeight.BOLD),
                ft.Text(Format.duration(self.report.duration_sec)),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_failed(self) -> ft.Control:
        remaining_minutes = math.ceil(self.report.remaining_sec / self.SECONDS_PER_MINUTE)
        return ft.Column(
            [
                ft.Text(self.report.subject),
                ft.Text("ยังไม่ได้ไข่", weight=ft.FontWeight.BOLD),
                ft.Text(f"อ่านไป {Format.duration(self.report.duration_sec)}"),
                ft.Text(f"ต้องอ่านอีก {remaining_minutes} นาที"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )