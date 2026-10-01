from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import flet as ft
from app.dto import PlayerDTO
from app.errors import ValidationError
from ui.core.base_view import BaseView
from ui.core.theme import Theme
from ui.core.widgets import PixelButton
from ui.landing.howto_popup import HowToPopup
from ui.landing.player_picker import PlayerPicker

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class LandingView(BaseView):
    route: ClassVar[str] = "/"
    requires_player: ClassVar[bool] = False

    def __init__(self, ctx: AppContext, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.picker: PlayerPicker | None = None
        self.howto: HowToPopup | None = None
        self._howto_img = ft.Image(
            src="buttons/howto_normal.PNG",
            height=50,
            fit="contain",
        )

    def build(self) -> ft.Control:
        players = self.ctx.players.list_players()
        self.picker = PlayerPicker(
            players=players,
            on_pick=self.pick_player,
            on_create=self.create_player,
        )

        howto_button = ft.Container(
            content=self._howto_img,
            on_click=lambda _: self.open_howto(),
            on_hover=self._on_howto_hover,
            ink=True,
            border_radius=8,
            alignment=ft.Alignment(0, 0),
        )

        picker_card = ft.Container(
            content=self.picker.control,
            bgcolor="black54",
            border_radius=16,
            padding=20,
        )

        return ft.Stack(
            [
                ft.Image(
                    src="backgrounds/landing_background.png",
                    fit="cover",
                    width=float("inf"),
                    height=float("inf"),
                ),
                ft.Container(
                    padding=24,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        [
                            ft.Image(
                                src="logo/cpego_logo.GIF",
                                height=120,
                                fit="contain",
                            ),
                            picker_card,
                            howto_button,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                ),
            ],
            expand=True,
        )

    def _on_howto_hover(self, e: ft.ControlEvent) -> None:
        """สลับรูปภาพปุ่ม HOW TO เมื่อเมาส์ชี้เข้า-ออก"""
        is_hovered = e.data == "true" or e.data is True
        self._howto_img.src = (
            "buttons/howto_hover.PNG" if is_hovered else "buttons/howto_normal.PNG"
        )
        self._howto_img.update()

    def pick_player(self, player: PlayerDTO) -> None:
        self.ctx.player = player
        self.ctx.nav.go("/lobby")

    def create_player(self, nickname: str) -> None:
        try:
            player = self.ctx.players.create_player(nickname)
        except ValidationError as error:
            if self.picker is not None:
                self.picker.show_error(error.message)
            return None
        self.pick_player(player)

    def open_howto(self) -> None:
        def close_howto() -> None:
            if (
                self.howto is not None
                and self.howto.control in self.ctx.page.overlay
            ):
                self.ctx.page.overlay.remove(self.howto.control)
                self.ctx.page.update()
                self.howto = None

        self.howto = HowToPopup(
            slides=HowToPopup.default_slides(), on_close=close_howto
        )
        self.ctx.page.overlay.append(self.howto.control)
        self.ctx.page.update()