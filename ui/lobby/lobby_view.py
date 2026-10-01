from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import flet as ft

from app.dto import SessionDTO
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.theme import Theme
from ui.core.widgets import PixelButton
from ui.focus.setup_popup import SetupPopup
from ui.landing.howto_popup import HowToPopup
from ui.lobby.image_button import ImageButton
from ui.lobby.sanctuary_scene import SanctuaryScene

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class LobbyView(BaseView):
    route: ClassVar[str] = "/lobby"

    MAP_WIDTH: ClassVar[float] = 1024
    MAP_HEIGHT: ClassVar[float] = 691
    MAX_SCALE: ClassVar[float] = 2.0
    BUTTON_HEIGHT: ClassVar[float] = 52
    PANEL_COLOR: ClassVar[str] = "black54"
    OVERLAY_COLOR: ClassVar[str] = "#99000000"
    POPUP_PADDING: ClassVar[int] = 20
    POPUP_RADIUS: ClassVar[int] = 16
    EMPTY_TEXT: ClassVar[str] = "ห้องยังว่างอยู่\nกด START แล้วอ่านให้ครบ 15 นาที เพื่อฟักไข่ตัวแรก!"

    def __init__(
        self,
        ctx: AppContext,
        **params: object,
    ) -> None:
        super().__init__(ctx, **params)
        self.scene: SanctuaryScene | None = None
        self.setup: SetupPopup | None = None
        self.howto: HowToPopup | None = None
        self.status_text: ft.Text | None = None
        self.empty_hint: ft.Container | None = None
        self._overlay: ft.Control | None = None

    def build(self) -> ft.Control:
        self.scene = SanctuaryScene(
            width=self.MAP_WIDTH,
            height=self.MAP_HEIGHT,
        )

        viewer = ft.InteractiveViewer(
            width=self._viewport_width(),
            height=self._viewport_height(),
            constrained=False,
            pan_enabled=True,
            scale_enabled=True,
            min_scale=self._minimum_scale(),
            max_scale=self.MAX_SCALE,
            boundary_margin=ft.Margin.all(0),
            content=self.scene.control,
        )

        self.status_text = ft.Text("", color=ft.Colors.WHITE, size=14)
        self.empty_hint = ft.Container(
            content=ft.Text(
                self.EMPTY_TEXT,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=self.PANEL_COLOR,
            border_radius=12,
            padding=16,
            visible=False,
        )

        return ft.Stack(
            controls=[
                ft.Container(
                    expand=True,
                    bgcolor=ft.Colors.BLACK,
                    alignment=ft.Alignment.CENTER,
                    content=viewer,
                ),
                ft.Container(
                    content=self.empty_hint,
                    alignment=ft.Alignment.CENTER,
                    left=0,
                    right=0,
                    top=0,
                    bottom=0,
                ),
                ft.Container(content=self._build_top_bar(), left=0, right=0, top=0),
                ft.Container(content=self._build_bottom_bar(), left=0, right=0, bottom=0),
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

        self.scene.load(pets)
        self.scene.start(self.ctx.page)

    def on_leave(self) -> None:
        if self.scene is not None:
            self.scene.stop()
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
        self._open_overlay(self.howto.control)

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
            self.status_text.value = f"{nickname} · สัตว์ในห้อง {pet_count} ตัว"
            self.status_text.update()
        if self.empty_hint is not None:
            self.empty_hint.visible = pet_count == 0
            self.empty_hint.update()

    def _build_top_bar(self) -> ft.Control:
        switch_button = ft.TextButton(
            content=ft.Text("เปลี่ยนผู้เล่น", color=ft.Colors.WHITE),
            on_click=self._handle_switch,
        )
        return ft.Container(
            content=ft.Row(
                controls=[self.status_text, switch_button],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=self.PANEL_COLOR,
            padding=ft.Padding.symmetric(horizontal=12, vertical=4),
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
        howto_button = ImageButton(
            "buttons/howto_normal.PNG",
            "buttons/howto_hover.PNG",
            self.open_howto,
            self.BUTTON_HEIGHT,
            "HOW TO",
        )
        group_button = PixelButton("GROUP STUDY", self.start_group)
        history_button = PixelButton("HISTORY", self.open_history, variant="secondary")
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[start_button.control, dex_button.control],
                        alignment=ft.MainAxisAlignment.CENTER,
                        wrap=True,
                    ),
                    ft.Row(
                        controls=[howto_button.control, group_button.control, history_button.control],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        wrap=True,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                tight=True,
            ),
            bgcolor=self.PANEL_COLOR,
            padding=12,
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
        self._overlay = ft.Container(
            content=card,
            bgcolor=self.OVERLAY_COLOR,
            alignment=ft.Alignment.CENTER,
            padding=16,
            expand=True,
        )
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

    def _viewport_width(self) -> float:
        page_width = self.ctx.page.width or self.MAP_WIDTH
        return min(page_width, self.MAP_WIDTH)

    def _viewport_height(self) -> float:
        page_height = self.ctx.page.height or self.MAP_HEIGHT
        return min(page_height, self.MAP_HEIGHT)

    def _minimum_scale(self) -> float:
        page_width = self.ctx.page.width or self.MAP_WIDTH
        page_height = self.ctx.page.height or self.MAP_HEIGHT

        if page_width < self.MAP_WIDTH:
            return page_height / self.MAP_HEIGHT

        return 1.0
