from __future__ import annotations
from typing import Callable
import flet as ft
from app.dto import PlayerDTO
from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme

MAX_NICKNAME_LENGTH = 20

class PlayerPicker(BaseWidget):
    def __init__(
        self,
        players: list[PlayerDTO],
        on_pick: Callable[[PlayerDTO], None],
        on_create: Callable[[str], None],
    ) -> None:
        super().__init__()
        self.players = players
        self.on_pick = on_pick
        self.on_create = on_create
        self.nickname_field: ft.TextField | None = None
        self.error_text: ft.Text | None = None

    def build(self) -> ft.Control:
        self.nickname_field = ft.TextField(label="ชื่อเล่นใหม่", max_length=MAX_NICKNAME_LENGTH)
        self.error_text = ft.Text("", color=Theme.ERROR, visible=False)
        player_rows: list[ft.Control] = [
            ft.ListTile(
                title=ft.Text(player.nickname),
                on_click=lambda _, selected=player: self.on_pick(selected),
            )
            for player in self.players
        ]
        return ft.Column(
            [
                ft.Text("เลือกผู้เล่น", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT),
                ft.Column(player_rows, scroll=ft.ScrollMode.AUTO, height=200),
                ft.Divider(),
                self.nickname_field,
                self.error_text,
                ft.FilledButton(
                    content=ft.Text("CREATE", color=ft.Colors.WHITE),
                    style=ft.ButtonStyle(
                    bgcolor=Theme.PRIMARY,
                    ),
                    on_click=lambda _: self.on_create(self.nickname_field.value or ""),
                )
            ]
        )

    def show_error(self, message: str) -> None:
        if self.error_text is not None:
            self.error_text.value = message
            self.error_text.visible = True
            # ✅ เช็กว่า control อยู่บน page แล้วหรือยังก่อนสั่ง update / refresh
            if self.error_text.page is not None:
                self.error_text.update()

