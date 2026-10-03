from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import flet as ft
from app.dto import PlayerDTO
from app.errors import ValidationError
from ui.core.base_view import BaseView
from ui.core.theme import Theme
from ui.core.volume_control import VolumeControl
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
        self._howto_overlay: ft.Control | None = None
        self.volume_control: VolumeControl | None = None
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
            sound=self.ctx.sound,
        )
        self.volume_control = VolumeControl(self.ctx.sound)

        howto_button = ft.Container(
            content=self._howto_img,
            on_click=lambda _: self.open_howto(),
            on_hover=self._on_howto_hover,
            ink=True,
            border_radius=8,
            alignment=ft.Alignment(0, 0),
        )
        self.ctx.sound.bind_button(howto_button)

        picker_card = ft.Container(
            content=self.picker.control,
            bgcolor=Theme.PANEL_COLOR,
            border_radius=Theme.PANEL_RADIUS,
            padding=Theme.PANEL_PADDING,
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
                    padding=Theme.PAGE_PADDING,
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
                        spacing=Theme.SPACING,
                    ),
                ),
                ft.Container(
                    content=self.volume_control.control,
                    height=48,
                    bgcolor=Theme.PANEL_COLOR,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=4),
                    right=0,
                    top=0,
                ),
            ],
            expand=True,
        )

    def _on_howto_hover(self, e: ft.ControlEvent) -> None:
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
                self._howto_overlay is not None
                and self._howto_overlay in self.ctx.page.overlay
            ):
                self.ctx.page.overlay.remove(self._howto_overlay)
                self.ctx.page.update()
            self.howto = None
            self._howto_overlay = None

        self.howto = HowToPopup(
            slides=HowToPopup.default_slides(),
            on_close=close_howto,
            sound=self.ctx.sound,
        )
        self._howto_overlay = self.howto.as_overlay()
        self.ctx.page.overlay.append(self._howto_overlay)
        self.ctx.page.update()