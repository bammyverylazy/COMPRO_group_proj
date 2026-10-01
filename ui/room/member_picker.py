from __future__ import annotations

from functools import partial
from typing import Callable, ClassVar

import flet as ft

from app.dto import PlayerDTO
from app.errors import AppError
from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme
from ui.core.widgets import PixelButton


class MemberPicker(BaseWidget):
    LIST_HEIGHT: ClassVar[int] = 220
    FIELD_LABEL: ClassVar[str] = "เพิ่มชื่อเล่นใหม่"
    MAX_NICKNAME: ClassVar[int] = 20

    def __init__(
        self,
        players: list[PlayerDTO],
        on_create: Callable[[str], PlayerDTO],
        max_members: int,
    ) -> None:
        super().__init__()
        self.players: list[PlayerDTO] = list(players)
        self.on_create: Callable[[str], PlayerDTO] = on_create
        self.max_members: int = max_members
        self.selected_ids: set[int] = set()
        self.nickname_field: ft.TextField | None = None
        self._list: ft.Column | None = None
        self._count_text: ft.Text | None = None
        self._error_text: ft.Text | None = None

    def build(self) -> ft.Control:
        self._count_text = ft.Text("", color=ft.Colors.WHITE)
        self._list = ft.Column(controls=self._rows(), scroll=ft.ScrollMode.AUTO, height=self.LIST_HEIGHT, spacing=0)
        self.nickname_field = ft.TextField(
            label=self.FIELD_LABEL,
            max_length=self.MAX_NICKNAME,
            on_submit=self._handle_submit,
            expand=True,
        )
        self._error_text = ft.Text("", color=Theme.ERROR, visible=False)
        add_button = PixelButton("ADD", self.add_player, variant="secondary")
        self._sync_count()
        return ft.Column(
            controls=[
                self._count_text,
                self._list,
                ft.Row(controls=[self.nickname_field, add_button.control], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                self._error_text,
            ],
            spacing=8,
            tight=True,
        )

    def toggle(self, player_id: int) -> None:
        if player_id in self.selected_ids:
            self.selected_ids.discard(player_id)
        elif len(self.selected_ids) < self.max_members:
            self.selected_ids.add(player_id)
        self._render()

    def add_player(self) -> None:
        if self.nickname_field is None:
            return
        nickname = (self.nickname_field.value or "").strip()
        try:
            player = self.on_create(nickname)
        except AppError as error:
            self._show_error(error.message)
            return
        self.players.append(player)
        self.nickname_field.value = ""
        if len(self.selected_ids) < self.max_members:
            self.selected_ids.add(player.id)
        self._show_error("")
        self._render()

    @property
    def selected(self) -> list[int]:
        return [player.id for player in self.players if player.id in self.selected_ids]

    def _rows(self) -> list[ft.Control]:
        return [
            ft.Checkbox(
                label=player.nickname,
                value=player.id in self.selected_ids,
                on_change=partial(self._handle_toggle, player.id),
                label_style=ft.TextStyle(color=ft.Colors.WHITE),
            )
            for player in self.players
        ]

    def _handle_toggle(self, player_id: int, event: ft.ControlEvent) -> None:
        self.toggle(player_id)

    def _handle_submit(self, event: ft.ControlEvent) -> None:
        self.add_player()

    def _render(self) -> None:
        if self._list is not None:
            self._list.controls = self._rows()
        self._sync_count()
        self.refresh()

    def _sync_count(self) -> None:
        if self._count_text is not None:
            self._count_text.value = f"เลือกแล้ว {len(self.selected_ids)} / {self.max_members} คน"

    def _show_error(self, message: str) -> None:
        if self._error_text is None:
            return
        self._error_text.value = message
        self._error_text.visible = bool(message)
        self.refresh()
