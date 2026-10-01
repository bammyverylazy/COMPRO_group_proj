from __future__ import annotations

from typing import Any, ClassVar

import flet as ft

from app.dto import SessionReport
from ui.core.base_view import BaseView
from ui.core.widgets import PixelButton
from ui.result.result_card import ResultCard


class ResultView(BaseView):
    route: ClassVar[str] = "/result"

    def __init__(self, ctx: Any, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.reports: list[SessionReport] = []
        self.cards: list[ResultCard] = []

    def build(self) -> ft.Control:
        controls: list[ft.Control] = [
            ft.Text("RESULT", size=28, weight=ft.FontWeight.BOLD),
        ]
        controls.extend(card.build() for card in self.cards)
        controls.append(PixelButton("RETURN TO LOBBY", on_click=self.return_to_lobby).control)
        return ft.Column(controls, spacing=12, scroll=ft.ScrollMode.AUTO)

    def on_enter(self) -> None:
        session_id = self.params.get("session_id")
        room_id = self.params.get("room_id")

        if session_id is not None:
            self.reports = [self.ctx.analytics.session_report(int(session_id))]
        elif room_id is not None:
            self.reports = self.ctx.analytics.room_reports(int(room_id))
        else:
            self.reports = []

        self.cards = []
        for report in self.reports:
            player = self.ctx.players.get_player(report.player_id)
            self.cards.append(ResultCard(report=report, nickname=player.nickname))

    def return_to_lobby(self) -> None:
        self.ctx.nav.go("/lobby")