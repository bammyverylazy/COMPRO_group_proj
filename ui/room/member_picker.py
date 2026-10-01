from __future__ import annotations

from typing import Callable, ClassVar

import flet as ft

from app.dto import PlayerDTO
from app.errors import AppError
from ui.core.base_widget import BaseWidget
from ui.core.widgets import PixelButton


class MemberPicker(BaseWidget):
    LIST_HEIGHT: ClassVar[int] = 240

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
        self._rows: ft.Column | None = None
        self._checkboxes: dict[int, ft.Checkbox] = {}

    def build(self) -> ft.Control:
        self.nickname_field = ft.TextField(
            label="ชื่อเล่นใหม่",
            expand=True,
            on_submit=lambda _: self.add_player(),
        )
        self._rows = ft.Column(
            [self._build_row(player) for player in self.players],
            height=self.LIST_HEIGHT,
            scroll=ft.ScrollMode.AUTO,
        )
        add_button = PixelButton("ADD", on_click=lambda _: self.add_player()).build()
        return ft.Column([self._rows, ft.Row([self.nickname_field, add_button])])

    def toggle(self, player_id: int) -> None:
        if player_id in self.selected_ids:
            self.selected_ids.discard(player_id)
        elif len(self.selected_ids) < self.max_members:
            self.selected_ids.add(player_id)
        self._sync_checkbox(player_id)

    def add_player(self) -> None:
        nickname = self.nickname_field.value.strip()
        try:
            player = self.on_create(nickname)
        except AppError as error:
            self.nickname_field.error_text = error.message
            self.nickname_field.update()
            return
        self.players.append(player)
        self.toggle(player.id)
        self._rows.controls.append(self._build_row(player))
        self.nickname_field.value = ""
        self.nickname_field.error_text = None
        self._rows.update()
        self.nickname_field.update()

    @property
    def selected(self) -> list[int]:
        return sorted(self.selected_ids)

    def _build_row(self, player: PlayerDTO) -> ft.Control:
        checkbox = ft.Checkbox(
            label=player.nickname,
            value=player.id in self.selected_ids,
            on_change=lambda _, player_id=player.id: self.toggle(player_id),
        )
        self._checkboxes[player.id] = checkbox
        return checkbox

    def _sync_checkbox(self, player_id: int) -> None:
        checkbox = self._checkboxes.get(player_id)
        if checkbox is None:
            return
        checkbox.value = player_id in self.selected_ids
        checkbox.update()