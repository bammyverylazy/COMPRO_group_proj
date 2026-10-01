from __future__ import annotations

from typing import Any, ClassVar, TYPE_CHECKING

import flet as ft

from app.errors import AppError, ValidationError
from ui.core.base_view import BaseView
from ui.core.widgets import PixelButton
from ui.room.member_picker import MemberPicker

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class RoomSetupView(BaseView):
    route: ClassVar[str] = "/room/setup"
    TITLE_SIZE: ClassVar[int] = 28

    def __init__(self, ctx: AppContext, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.picker: MemberPicker | None = None
        self.subject_field: ft.TextField | None = None
        self.error_text: ft.Text | None = None

    def build(self) -> ft.Control:
        self.picker = MemberPicker(
            self.ctx.players.list_players(),
            self.ctx.players.create_player,
            self.ctx.settings.max_room_members,
        )
        self.picker.toggle(self.ctx.player.id)
        self.subject_field = ft.TextField(label="ชื่อวิชา")
        self.error_text = ft.Text("", color=ft.Colors.RED)
        start_button = PixelButton("START", on_click=lambda _: self.start()).build()
        back_button = PixelButton("BACK", on_click=lambda _: self.back()).build()
        return ft.Column(
            [
                ft.Text("GROUP STUDY", size=self.TITLE_SIZE),
                self.picker.build(),
                self.subject_field,
                self.error_text,
                ft.Row([start_button, back_button]),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def start(self) -> None:
        self.error_text.value = ""
        try:
            room = self.ctx.rooms.create_room(
                self.picker.selected,
                self.subject_field.value.strip(),
            )
        except ValidationError as error:
            self.error_text.value = error.message
            self.error_text.update()
            return
        except AppError as error:
            self.show_error(error)
            return
        self.ctx.navigator.go("/room", room_id=room.id)

    def back(self) -> None:
        self.ctx.navigator.go("/lobby")