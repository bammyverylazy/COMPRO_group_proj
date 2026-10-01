from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar

import flet as ft

from app.domain.enums import RoomStatus
from app.dto import RoomDTO, RoomStopResult, TierOdds
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.format import Format
from ui.core.widgets import ConfirmDialog, PixelButton
from ui.focus.cpego_bot import CpegoBot, CpegoMessage
from ui.focus.cpego_bubble import CpegoBubble
from ui.focus.stopwatch_timer import StopwatchTimer
from ui.hatch.egg_odds_panel import EggOddsPanel
from ui.room.member_list import MemberList

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class RoomFocusView(BaseView):
    route: ClassVar[str] = "/room"
    BACKGROUND_PATH: ClassVar[str] = "backgrounds/room_background.png"
    PANEL_COLOR: ClassVar[str] = "black54"
    TIME_SIZE: ClassVar[int] = 64
    PANEL_WIDTH: ClassVar[int] = 400
    INITIAL_TIME: ClassVar[str] = "00:00"
    CONFIRM_TITLE: ClassVar[str] = "หยุดตอนนี้ ทุกคนในห้องจะได้ผลเดียวกัน ถ้ายังไม่ครบ 15 นาทีจะไม่มีใครได้ไข่"

    def __init__(self, ctx: AppContext, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.room: RoomDTO | None = None
        self.timer: StopwatchTimer | None = None
        self.time_text: ft.Text | None = None
        self.members: MemberList | None = None
        self.odds_panel: EggOddsPanel | None = None
        self.bot: CpegoBot | None = None
        self.bubble: CpegoBubble | None = None
        self.confirm: ConfirmDialog | None = None
        self.subject_text: ft.Text | None = None
        self.members_slot: ft.Container | None = None

    def build(self) -> ft.Control:
        brackets: list[TierOdds] = self.ctx.tiers.list_odds()
        self.subject_text = ft.Text("", size=20, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
        self.time_text = ft.Text(self.INITIAL_TIME, size=self.TIME_SIZE, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.members_slot = ft.Container()
        self.odds_panel = EggOddsPanel(brackets)
        self.bot = CpegoBot(brackets)
        self.bubble = CpegoBubble()
        self.confirm = ConfirmDialog(self.CONFIRM_TITLE, on_yes=self.confirm_stop)
        stop_button = PixelButton("STOP", self.ask_stop, variant="danger")

        panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("GROUP STUDY", size=14, color="white70"),
                    self.subject_text,
                    self.time_text,
                    self.members_slot,
                    ft.Container(content=self.odds_panel.control, width=self.PANEL_WIDTH),
                    stop_button.control,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=self.PANEL_COLOR,
            border_radius=16,
            padding=16,
        )

        return ft.Stack(
            controls=[
                ft.Image(src=self.BACKGROUND_PATH, fit=ft.BoxFit.COVER, width=float("inf"), height=float("inf")),
                ft.Container(content=panel, alignment=ft.Alignment.CENTER, padding=16, left=0, right=0, top=0, bottom=0),
                ft.Container(content=self.bubble.control, right=16, bottom=16),
            ],
            expand=True,
        )

    def on_enter(self) -> None:
        room_id = self.params.get("room_id")
        if room_id is None:
            self.ctx.nav.go("/lobby")
            return
        try:
            room = self.ctx.rooms.get_room(int(room_id))
        except AppError as error:
            self.show_error(error)
            return
        if room.status is RoomStatus.READY_TO_HATCH:
            self.ctx.nav.go("/hatch", room_id=room.id)
            return
        if room.status is not RoomStatus.RUNNING:
            self.ctx.nav.go("/result", room_id=room.id)
            return
        self.room = room
        self._show_room(room)
        self.timer = StopwatchTimer(self.ctx.clock, self._started_at(room), self.on_tick)
        self.timer.start(self.ctx.page)
        if self.bot is not None and self.bubble is not None:
            self.bubble.show(self.ctx.page, self.bot.greeting(room.subject))

    def on_leave(self) -> None:
        if self.timer is not None:
            self.timer.stop()

    def on_tick(self, elapsed_sec: int) -> None:
        if self.time_text is None or self.members is None or self.odds_panel is None:
            return
        self.time_text.value = Format.clock(elapsed_sec)
        self.time_text.update()
        self.members.set_egg_odds(self.ctx.tiers.odds_for(elapsed_sec))
        self.odds_panel.set_current(elapsed_sec)
        self._announce(elapsed_sec)

    def ask_stop(self) -> None:
        if self.confirm is not None:
            self.confirm.open(self.ctx.page)

    def confirm_stop(self) -> None:
        if self.room is None:
            return
        try:
            result: RoomStopResult = self.ctx.rooms.stop(self.room.id)
        except AppError as error:
            self.show_error(error)
            return
        if self.timer is not None:
            self.timer.stop()
        route = "/hatch" if result.status is RoomStatus.READY_TO_HATCH else "/result"
        self.ctx.nav.go(route, room_id=result.room_id)

    def _show_room(self, room: RoomDTO) -> None:
        if self.subject_text is not None:
            self.subject_text.value = f"{room.subject} · {len(room.members)} คน"
            self.subject_text.update()
        if self.members_slot is not None:
            self.members = MemberList(room.members)
            self.members_slot.content = self.members.control
            self.members_slot.update()

    def _started_at(self, room: RoomDTO) -> datetime:
        return datetime.fromisoformat(room.started_at)

    def _announce(self, elapsed_sec: int) -> None:
        if self.bot is None or self.bubble is None:
            return
        message: CpegoMessage | None = self.bot.check(elapsed_sec)
        if message is not None:
            self.bubble.show(self.ctx.page, message)
