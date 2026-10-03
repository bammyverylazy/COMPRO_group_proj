from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, TYPE_CHECKING

import flet as ft

from app.domain.enums import SessionStatus
from app.dto import SessionDTO, StopResult, TierOdds
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.format import Format
from ui.core.theme import Theme
from ui.core.volume_control import VolumeControl
from ui.core.widgets import ConfirmDialog, PixelButton
from ui.focus.cpego_bot import CpegoBot, CpegoMessage
from ui.focus.cpego_bubble import CpegoBubble
from ui.focus.egg_view import EggView
from ui.focus.stopwatch_timer import StopwatchTimer
from ui.hatch.egg_odds_panel import EggOddsPanel

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class FocusView(BaseView):
    route: ClassVar[str] = "/focus"
    LOBBY_ROUTE: ClassVar[str] = "/lobby"
    HATCH_ROUTE: ClassVar[str] = "/hatch"
    RESULT_ROUTE: ClassVar[str] = "/result"
    BACKGROUND_PATH: ClassVar[str] = "backgrounds/focus_background.png"
    TIME_SIZE: ClassVar[int] = Theme.CLOCK_SIZE
    SUBJECT_SIZE: ClassVar[int] = Theme.HEADING_SIZE
    PANEL_WIDTH: ClassVar[int] = Theme.CONTENT_WIDTH
    SPACING: ClassVar[int] = Theme.SPACING
    BUBBLE_MARGIN: ClassVar[int] = Theme.PAGE_PADDING
    INITIAL_TIME: ClassVar[str] = "00:00"
    CONFIRM_TITLE: ClassVar[str] = "Stop studying? If you have not reached the minimum time, you will not get an egg."

    def __init__(self, ctx: AppContext, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.session: SessionDTO | None = None
        self.timer: StopwatchTimer | None = None
        self.time_text: ft.Text | None = None
        self.subject_text: ft.Text | None = None
        self.egg_view: EggView | None = None
        self.odds_panel: EggOddsPanel | None = None
        self.bot: CpegoBot | None = None
        self.bubble: CpegoBubble | None = None
        self.confirm: ConfirmDialog | None = None
        self.volume_control: VolumeControl | None = None

    def build(self) -> ft.Control:
        brackets: list[TierOdds] = self.ctx.tiers.list_odds()
        self.subject_text = ft.Text("", size=self.SUBJECT_SIZE, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
        self.time_text = ft.Text(
            self.INITIAL_TIME,
            size=self.TIME_SIZE,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        )
        self.egg_view = EggView()
        self.odds_panel = EggOddsPanel(brackets, text_color=ft.Colors.WHITE)
        self.bot = CpegoBot(brackets)
        self.bubble = CpegoBubble()
        self.confirm = ConfirmDialog(
            self.CONFIRM_TITLE,
            on_yes=self.confirm_stop,
            sound=self.ctx.sound,
        )
        self.volume_control = VolumeControl(self.ctx.sound)

        background: ft.Image = ft.Image(
            src=self.BACKGROUND_PATH,
            fit=ft.BoxFit.COVER,
            width=float("inf"),
            height=float("inf"),
        )
        return ft.Stack(
            controls=[
                background,
                self._build_content(),
                self._build_bubble_slot(),
                self._build_volume_bar(),
            ],
            expand=True,
        )

    def on_enter(self) -> None:
        session: SessionDTO | None = self._load_session()
        if session is None or self.bot is None or self.bubble is None:
            return
        self.session = session
        self._show_subject(session.subject)
        self.timer = StopwatchTimer(self.ctx.clock, self._started_at(session), self.on_tick)
        self.timer.start(self.ctx.page)
        self.bubble.show(self.ctx.page, self.bot.greeting(session.subject))

    def on_leave(self) -> None:
        if self.timer is not None:
            self.timer.stop()

    def on_tick(self, elapsed_sec: int) -> None:
        if self.time_text is None or self.egg_view is None or self.odds_panel is None:
            return
        self.time_text.value = Format.clock(elapsed_sec)
        self.time_text.update()
        self.egg_view.set_odds(self.ctx.tiers.odds_for(elapsed_sec))
        self.odds_panel.set_current(elapsed_sec)
        self._announce(elapsed_sec)

    def ask_stop(self) -> None:
        if self.confirm is None:
            return
        self.confirm.open(self.ctx.page)

    def confirm_stop(self) -> None:
        if self.session is None:
            return
        try:
            result: StopResult = self.ctx.focus.stop(self.session.id)
        except AppError as error:
            self.show_error(error)
            return
        route: str = self.HATCH_ROUTE if result.status is SessionStatus.READY_TO_HATCH else self.RESULT_ROUTE
        self.ctx.nav.go(route, session_id=result.session_id)

    def _build_content(self) -> ft.Control:
        stop_button: PixelButton = PixelButton(
            "STOP", self.ask_stop, variant="danger", sound=self.ctx.sound
        )
        panel = ft.Container(
            content=ft.Column(
                controls=[
                    self.subject_text,
                    self.time_text,
                    self.egg_view.control,
                    ft.Container(content=self.odds_panel.control, width=self.PANEL_WIDTH),
                    stop_button.control,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=self.SPACING,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=Theme.PANEL_COLOR,
            border_radius=Theme.PANEL_RADIUS,
            padding=Theme.PANEL_PADDING,
        )
        return ft.Container(
            content=panel,
            alignment=ft.Alignment.CENTER,
            padding=Theme.PAGE_PADDING,
            left=0,
            right=0,
            top=0,
            bottom=0,
        )

    def _build_bubble_slot(self) -> ft.Control:
        return ft.Container(
            content=self.bubble.control,
            right=self.BUBBLE_MARGIN,
            bottom=self.BUBBLE_MARGIN,
        )

    def _build_volume_bar(self) -> ft.Control:
        return ft.Container(
            content=self.volume_control.control,
            right=16,
            top=18,
        )

    def _load_session(self) -> SessionDTO | None:
        try:
            session: SessionDTO | None = self.ctx.focus.get_running(self.ctx.require_player().id)
        except AppError as error:
            self.show_error(error)
            return None
        if session is None or session.id != self.params.get("session_id"):
            self.ctx.nav.go(self.LOBBY_ROUTE)
            return None
        return session

    def _started_at(self, session: SessionDTO) -> datetime:
        if isinstance(session.started_at, datetime):
            return session.started_at
        return datetime.fromisoformat(session.started_at)

    def _show_subject(self, subject: str) -> None:
        if self.subject_text is None:
            return
        self.subject_text.value = subject
        self.subject_text.update()

    def _announce(self, elapsed_sec: int) -> None:
        if self.bot is None or self.bubble is None or self.egg_view is None:
            return
        message: CpegoMessage | None = self.bot.check(elapsed_sec)
        if message is None:
            return
        self.bubble.show(self.ctx.page, message)
        self.egg_view.wobble()