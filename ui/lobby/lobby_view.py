from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import flet as ft

from app.dto import SessionDTO
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.theme import Theme
from ui.focus.setup_popup import SetupPopup
from ui.landing.howto_popup import HowToPopup
from ui.lobby.image_button import ImageButton
from ui.lobby.sanctuary_scene import SanctuaryScene

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class LobbyView(BaseView):
    route: ClassVar[str] = "/lobby"

    BUTTON_HEIGHT: ClassVar[float] = 45
    PANEL_COLOR: ClassVar[str] = Theme.PANEL_COLOR
    OVERLAY_COLOR: ClassVar[str] = "#99000000"
    POPUP_PADDING: ClassVar[int] = 20
    POPUP_RADIUS: ClassVar[int] = 16
    BACKGROUND_PATH: ClassVar[str] = "backgrounds/landing_background.png"
    TOP_BAR_HEIGHT: ClassVar[float] = 48
    BOTTOM_BAR_HEIGHT: ClassVar[float] = 2 * BUTTON_HEIGHT + 8 + 2 * Theme.PANEL_PADDING
    EMPTY_TEXT: ClassVar[str] = (
        "Your room is empty.\nPress START and study for 15 minutes to hatch your first egg!"
    )

    def __init__(
        self,
        ctx: AppContext,
        **params: object,
    ) -> None:
        super().__init__(ctx, **params)
        self.setup: SetupPopup | None = None
        self.howto: HowToPopup | None = None
        self.status_text: ft.Text | None = None
        self.empty_hint: ft.Container | None = None
        self._overlay: ft.Control | None = None
        self.scene: SanctuaryScene | None = None

    def build(self) -> ft.Control:
        width, height = self._screen_size()
        self.scene = SanctuaryScene(
            width=width,
            height=height,
            top=self.TOP_BAR_HEIGHT,
            bottom=self.BOTTOM_BAR_HEIGHT,
        )
        self.status_text = ft.Text(
            "",
            color=ft.Colors.WHITE,
            size=Theme.BODY_SIZE,
        )

        self.empty_hint = ft.Container(
            content=ft.Text(
                self.EMPTY_TEXT,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=self.PANEL_COLOR,
            border_radius=12,
            padding=Theme.PAGE_PADDING,
            visible=False,
        )

        howto_button = ImageButton(
            "buttons/howto_normal.PNG",
            "buttons/howto_hover.PNG",
            self.open_howto,
            self.BUTTON_HEIGHT,
            "HOW TO",
        )
        history_button = ImageButton(
            "buttons/history_normal.PNG",
            "buttons/history_hover.PNG",
            self.open_history,
            self.BUTTON_HEIGHT,
            "HISTORY",
        )

        return ft.Stack(
            controls=[
                ft.Image(
                    src=self.BACKGROUND_PATH,
                    fit=ft.BoxFit.COVER,
                    width=float("inf"),
                    height=float("inf"),
                ),
                ft.Container(
                    content=self.scene.control,
                    left=0,
                    right=0,
                    top=0,
                    bottom=0,
                ),
                ft.Container(
                    content=self.empty_hint,
                    alignment=ft.Alignment.CENTER,
                    left=0,
                    right=0,
                    top=0,
                    bottom=0,
                ),
                ft.Container(
                    content=self._build_top_bar(),
                    left=0,
                    right=0,
                    top=0,
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            history_button.control,
                            howto_button.control,
                        ],
                        spacing=4,
                        tight=True,
                    ),
                    top=50,
                    right=16,
                ),
                ft.Container(
                    content=self._build_bottom_bar(),
                    left=0,
                    right=0,
                    bottom=0,
                ),
            ],
            expand=True,
        )

    def on_enter(self) -> None:
        player = self.ctx.require_player()

        try:
            running = self.ctx.focus.get_running(player.id)
            if running is not None:
                self._resume(running)
                return

            pets = self.ctx.sanctuary.list_pets(player.id)
        except AppError as error:
            self.show_error(error)
            return

        self._show_status(player.nickname, len(pets))

        if self.scene is None:
            return
        self.scene.resize(*self._screen_size())
        self.scene.load(pets)
        self.scene.start(self.ctx.page)
        self.ctx.page.on_resize = self._handle_resize

    def on_leave(self) -> None:
        if self.scene is not None:
            self.scene.stop()
        self.ctx.page.on_resize = None
        self._close_overlay()

    def start_focus(self) -> None:
        self.setup = SetupPopup(
            self.ctx,
            on_started=self.on_session_started,
            on_back=self._close_overlay,
        )
        self._open_overlay(self.setup.control)

    def on_session_started(self, session: SessionDTO) -> None:
        self._close_overlay()
        self.ctx.nav.go("/focus", session_id=session.id)

    def start_group(self) -> None:
        self.ctx.nav.go("/room/setup")

    def open_dex(self) -> None:
        self.ctx.nav.go("/dex")

    def open_history(self) -> None:
        self.ctx.nav.go("/history")

    def open_howto(self) -> None:
        self.howto = HowToPopup(
            slides=HowToPopup.default_slides(),
            on_close=self._close_overlay,
        )
        self._show_overlay(self.howto.as_overlay())

    def switch_player(self) -> None:
        self.ctx.player = None
        self.ctx.nav.go("/")

    def _resume(self, session: SessionDTO) -> None:
        if session.room_id is not None:
            self.ctx.nav.go("/room", room_id=session.room_id)
            return

        self.ctx.nav.go("/focus", session_id=session.id)

    def _show_status(self, nickname: str, pet_count: int) -> None:
        if self.status_text is not None:
            self.status_text.value = f"{nickname} · {pet_count} creatures"
            self.status_text.update()

        if self.empty_hint is not None:
            self.empty_hint.visible = pet_count == 0
            self.empty_hint.update()

    def _build_top_bar(self) -> ft.Control:
        switch_button = ft.TextButton(
            content=ft.Text(
                "SWITCH PLAYER",
                color=ft.Colors.WHITE,
            ),
            on_click=self._handle_switch,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    self.status_text,
                    switch_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            height=self.TOP_BAR_HEIGHT,
            bgcolor=self.PANEL_COLOR,
            padding=ft.Padding.symmetric(
                horizontal=12,
                vertical=4,
            ),
        )

    def _build_bottom_bar(self) -> ft.Control:
        start_button = ImageButton(
            "buttons/startfocus_normal.PNG",
            "buttons/startfocus_hover.PNG",
            self.start_focus,
            self.BUTTON_HEIGHT,
            "START",
        )

        dex_button = ImageButton(
            "buttons/eggdex_normal.PNG",
            "buttons/eggdex_hover.PNG",
            self.open_dex,
            self.BUTTON_HEIGHT,
            "EGGDEX",
        )

        group_button = ImageButton(
            "buttons/groupstudy_normal.PNG",
            "buttons/groupstudy_hover.PNG",
            self.start_group,
            self.BUTTON_HEIGHT,
            "GROUP STUDY",
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            start_button.control,
                            dex_button.control,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        wrap=True,
                    ),
                    ft.Row(
                        controls=[
                            group_button.control,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        wrap=True,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                tight=True,
            ),
            height=self.BOTTOM_BAR_HEIGHT,
            bgcolor=self.PANEL_COLOR,
            padding=Theme.PANEL_PADDING,
        )

    def _handle_switch(self, event: ft.ControlEvent) -> None:
        self.switch_player()

    def _open_overlay(self, content: ft.Control) -> None:
        self._close_overlay()

        card = ft.Container(
            content=content,
            bgcolor=Theme.BACKGROUND,
            border_radius=self.POPUP_RADIUS,
            padding=self.POPUP_PADDING,
        )

        self._show_overlay(
            ft.Container(
                content=card,
                bgcolor=self.OVERLAY_COLOR,
                alignment=ft.Alignment.CENTER,
                padding=Theme.PAGE_PADDING,
                expand=True,
            )
        )

    def _show_overlay(self, overlay: ft.Control) -> None:
        self._close_overlay()
        self._overlay = overlay
        self.ctx.page.overlay.append(self._overlay)
        self.ctx.page.update()

    def _close_overlay(self) -> None:
        if self._overlay is None:
            return

        if self._overlay in self.ctx.page.overlay:
            self.ctx.page.overlay.remove(self._overlay)

        self._overlay = None
        self.setup = None
        self.howto = None
        self.ctx.page.update()

    def _screen_size(self) -> tuple[float, float]:
        width = self.ctx.page.width or Theme.WINDOW_WIDTH
        height = self.ctx.page.height or Theme.WINDOW_HEIGHT
        return float(width), float(height)

    def _handle_resize(self, event: ft.ControlEvent) -> None:
        if self.scene is not None:
            self.scene.resize(*self._screen_size())
