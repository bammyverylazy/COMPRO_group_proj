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

    def build(self) -> ft.Control:
        players = self.ctx.players.list_players()
        self.picker = PlayerPicker(
            players=players,
            on_pick=self.pick_player,
            on_create=self.create_player,
        )
        howto_button = PixelButton(
            text="HOW TO PLAY",
            on_click=self.open_howto,
            variant="secondary",
        )
        return ft.Container(
            bgcolor=Theme.BACKGROUND,
            padding=24,
            content=ft.Column(
                [
                    ft.Text("CPE Egg Hatch", size=32, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                    self.picker.control,
                    howto_button.control,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

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
            if self.howto is not None and self.howto.control in self.ctx.page.overlay:
                self.ctx.page.overlay.remove(self.howto.control)
                self.ctx.page.update()
                self.howto = None

        self.howto = HowToPopup(slides=HowToPopup.default_slides(), on_close=close_howto)
        self.ctx.page.overlay.append(self.howto.control)
        self.ctx.page.update()

