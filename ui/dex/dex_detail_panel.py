from __future__ import annotations

from typing import ClassVar

import flet as ft

from app.dto import DexEntry
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.theme import Theme


class DexDetailPanel(BaseWidget):
    IMAGE_SIZE: ClassVar[int] = 140
    PANEL_COLOR: ClassVar[str] = "black54"
    EMPTY_TEXT: ClassVar[str] = "กดเลือกสัตว์เพื่อดูรายละเอียด"
    LOCKED_NAME: ClassVar[str] = "???"

    def __init__(self, entry: DexEntry | None = None) -> None:
        super().__init__()
        self.entry: DexEntry | None = entry
        self._body: ft.Column | None = None

    def build(self) -> ft.Control:
        self._body = ft.Column(
            controls=self._content(),
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            tight=True,
        )
        return ft.Container(
            content=self._body,
            bgcolor=self.PANEL_COLOR,
            border_radius=16,
            padding=16,
        )

    def show(self, entry: DexEntry) -> None:
        self.entry = entry
        if self._body is None:
            return
        self._body.controls = self._content()
        self.refresh()

    def _content(self) -> list[ft.Control]:
        if self.entry is None:
            return [ft.Text(self.EMPTY_TEXT, color=ft.Colors.WHITE)]
        if not self.entry.unlocked:
            return self._locked_content(self.entry)
        return self._unlocked_content(self.entry)

    def _unlocked_content(self, entry: DexEntry) -> list[ft.Control]:
        species = entry.species
        first_text = entry.first_hatched_at.astimezone().strftime("%d/%m/%Y %H:%M") if entry.first_hatched_at else "-"
        subjects_text = ", ".join(entry.subjects) if entry.subjects else "-"
        controls: list[ft.Control] = [
            ft.Image(src=species.sprite_path, width=self.IMAGE_SIZE, height=self.IMAGE_SIZE, fit=ft.BoxFit.CONTAIN),
            ft.Text(species.name, size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Row(
                controls=[self._chip(Format.tier_name(species.tier), Theme.PRIMARY), self._rarity_chip(entry)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            self._line("Level", str(entry.level)),
            self._line("ฟักได้", f"{entry.times_hatched} ครั้ง"),
            self._line("ได้ครั้งแรก", first_text),
            self._line("วิชาที่อ่านตอนได้", subjects_text),
        ]
        if species.description:
            controls.append(ft.Text(species.description, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER))
        return controls

    def _locked_content(self, entry: DexEntry) -> list[ft.Control]:
        species = entry.species
        return [
            ft.Image(
                src=species.sprite_path,
                width=self.IMAGE_SIZE,
                height=self.IMAGE_SIZE,
                fit=ft.BoxFit.CONTAIN,
                color=ft.Colors.BLACK,
                color_blend_mode=ft.BlendMode.SRC_IN,
                opacity=0.7,
            ),
            ft.Text(self.LOCKED_NAME, size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Row(
                controls=[self._chip(Format.tier_name(species.tier), Theme.PRIMARY), self._rarity_chip(entry)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text(
                f"ยังไม่ได้ปลดล็อก · ลองฟัก{Format.tier_name(species.tier)}ดูสิ",
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
        ]

    def _rarity_chip(self, entry: DexEntry) -> ft.Control:
        rarity = entry.species.rarity
        return self._chip(rarity.value.upper(), Theme.rarity_color(rarity))

    def _chip(self, text: str, color: str) -> ft.Control:
        return ft.Container(
            content=ft.Text(text, size=12, color=ft.Colors.WHITE),
            bgcolor=color,
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=10, vertical=2),
        )

    def _line(self, label: str, value: str) -> ft.Control:
        return ft.Row(
            controls=[
                ft.Text(label, size=13, color="white70"),
                ft.Text(value, size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.RIGHT),
            ],
            width=300,
        )
