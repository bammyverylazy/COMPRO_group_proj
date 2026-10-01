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
        controls: list[ft.Control] = [body]
        if self.report.room_id is not None:
            controls.insert(0, ft.Text(self.nickname, size=self.TITLE_SIZE))

        return ft.Container(
            content=ft.Column(
                controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=self.CARD_PADDING,
            border_radius=self.CARD_RADIUS,
            bgcolor=self.CARD_COLOR,
        )

    def _build_success(self) -> ft.Control:
        pet = self.report.pet
        if pet is None:
            pet_name = "สัตว์เลี้ยง"
            sprite_path = ""
            level = 0
            scale = 1.0
        else:
            pet_name = pet.species.name
            sprite_path = pet.species.sprite_path
            level = pet.level
            scale = pet.scale

        sprite_size = int(self.SPRITE_SIZE * scale)
        badge = "ตัวใหม่!" if bool(self.report.is_new) else f"LEVEL UP! Lv.{level}"
        tier_name = self.TIER_NAMES.get(self.report.tier, "ไข่") if self.report.tier is not None else "ไข่"

        return ft.Column(
            [
                ft.Text(self.report.subject),
                ft.Text(tier_name),
                ft.Image(src=sprite_path, width=sprite_size, height=sprite_size),
                ft.Text(pet_name),
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