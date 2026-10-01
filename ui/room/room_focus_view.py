from __future__ import annotations

from typing import Any, ClassVar, TYPE_CHECKING

import flet as ft

from app.domain.enums import RoomStatus
from app.dto import RoomDTO
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.format import Format
from ui.core.widgets import ConfirmDialog, PixelButton
from ui.focus.cpego_bot import CpegoBot
from ui.focus.cpego_bubble import CpegoBubble
from ui.focus.stopwatch_timer import StopwatchTimer
from ui.hatch.egg_odds_panel import EggOddsPanel
from ui.room.member_list import MemberList

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class RoomFocusView(BaseView):
    route: ClassVar[str] = "/room"
    TIME_SIZE: ClassVar[int] = 48
    CONFIRM_MESSAGE: ClassVar[str] = "ถ้าหยุดตอนนี้ ทุกคนจะได้ผลเดียวกัน"

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

    def build(self) -> ft.Control:
        stop_button = PixelButton("STOP", on_click=lambda _: self.ask_stop()).build()
        return ft.Column(
            [
                self.time_text,
                self.members.build(),
                self.odds_panel.build(),
                stop_button,
                self.bubble.build(),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )

    def on_enter(self) -> None:
        try:
            self.room = self.ctx.rooms.get(self.params["room_id"])
        except AppError as error:
            self.show_error(error)
            return
        brackets = self.ctx.tiers.list_odds()
        self.time_text = ft.Text(Format.clock(0), size=self.TIME_SIZE)
        self.members = MemberList(self.room.members)
        self.odds_panel = EggOddsPanel(brackets)
        self.bot = CpegoBot(brackets)
        self.bubble = CpegoBubble()
        self.timer = StopwatchTimer(self.ctx.clock, self.room.started_at, self.on_tick)
        self.confirm = ConfirmDialog(self.CONFIRM_MESSAGE, on_yes=self.confirm_stop)
        self.timer.start(self.ctx.page)
        self.bubble.show(self.ctx.page, self.bot.greeting(self.room.subject))

    def on_leave(self) -> None:
        if self.timer is not None:
            self.timer.stop()

    def on_tick(self, elapsed_sec: int) -> None:
        self.time_text.value = Format.clock(elapsed_sec)
        self.time_text.update()
        self.members.set_egg_odds(self.ctx.tiers.odds_at(elapsed_sec))
        self.odds_panel.set_current(elapsed_sec)
        message = self.bot.check(elapsed_sec)
        if message is not None:
            self.bubble.show(self.ctx.page, message)

    def ask_stop(self) -> None:
        self.confirm.open(self.ctx.page)

    def confirm_stop(self) -> None:
        try:
            result = self.ctx.rooms.stop(self.room.id)
        except AppError as error:
            self.show_error(error)
            return
        route = "/result" if result.status is RoomStatus.FAILED else "/hatch"
        self.ctx.navigator.go(route, room_id=result.room_id)

