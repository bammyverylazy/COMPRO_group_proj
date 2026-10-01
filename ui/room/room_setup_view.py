from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import flet as ft

from app.dto import PlayerDTO
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.theme import Theme
from ui.core.widgets import PixelButton
from ui.room.member_picker import MemberPicker

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class RoomSetupView(BaseView):
    route: ClassVar[str] = "/room/setup"
    BACKGROUND_PATH: ClassVar[str] = "backgrounds/room_background.png"
    PANEL_COLOR: ClassVar[str] = Theme.PANEL_COLOR
    TITLE: ClassVar[str] = "GROUP STUDY"
    HINT: ClassVar[str] = "Everyone studies together and shares one fate: stop before 15 minutes and nobody gets an egg."

    def __init__(self, ctx: AppContext, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.picker: MemberPicker | None = None
        self.subject_field: ft.TextField | None = None
        self.error_text: ft.Text | None = None

    def build(self) -> ft.Control:
        self.picker = MemberPicker(
            players=self.ctx.players.list_players(),
            on_create=self._create_player,
            max_members=self.ctx.settings.max_room_members,
        )
        player = self.ctx.player
        if player is not None:
            self.picker.selected_ids.add(player.id)
        self.subject_field = ft.TextField(
            label="Subject",
            on_submit=self._handle_submit,
            color=ft.Colors.WHITE,
            label_style=ft.TextStyle(color=ft.Colors.WHITE_70),
            cursor_color=ft.Colors.WHITE,
            border_color=ft.Colors.WHITE_70,
            focused_border_color=Theme.ACCENT,
        )
        self.error_text = ft.Text("", color=Theme.ERROR, visible=False)
        back_button = PixelButton("BACK", self.back, variant="secondary")
        start_button = PixelButton("START", self.start)

        panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(self.TITLE, size=Theme.TITLE_SIZE, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(self.HINT, size=Theme.SMALL_SIZE, color=ft.Colors.WHITE),
                    self.picker.control,
                    self.subject_field,
                    self.error_text,
                    ft.Row(
                        controls=[back_button.control, start_button.control],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=10,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=self.PANEL_COLOR,
            border_radius=Theme.PANEL_RADIUS,
            padding=Theme.PAGE_PADDING,
        )

        return ft.Stack(
            controls=[
                ft.Image(src=self.BACKGROUND_PATH, fit=ft.BoxFit.COVER, width=float("inf"), height=float("inf")),
                ft.Container(content=panel, alignment=ft.Alignment.CENTER, padding=Theme.PAGE_PADDING, left=0, right=0, top=0, bottom=0),
            ],
            expand=True,
        )

    def start(self) -> None:
        if self.picker is None or self.subject_field is None:
            return
        try:
            room = self.ctx.rooms.create_room(self.picker.selected, self.subject_field.value or "")
        except AppError as error:
            self._show_error(error.message)
            return
        self.ctx.nav.go("/room", room_id=room.id)

    def back(self) -> None:
        self.ctx.nav.go("/lobby")

    def _create_player(self, nickname: str) -> PlayerDTO:
        return self.ctx.players.create_player(nickname)

    def _handle_submit(self, event: ft.ControlEvent) -> None:
        self.start()

    def _show_error(self, message: str) -> None:
        if self.error_text is None:
            return
        self.error_text.value = message
        self.error_text.visible = True
        self.error_text.update()
