from __future__ import annotations

from typing import Any, ClassVar

import flet as ft

from app.dto import SessionReport
from app.errors import AppError
from ui.core.theme import Theme
from ui.core.base_view import BaseView
from ui.result.result_card import ResultCard

BG_NORMAL = "#E8C88A"
BG_HOVER = "#FFE8AD"
BORDER_COLOR = "#6D4348"
TEXT_COLOR = "#734547"
FONT_PIXEL = getattr(Theme, "FONT_PIXEL", "Pixel")


class ResultView(BaseView):
    BACKGROUND_PATH: ClassVar[str] = "backgrounds/result_background.png"
    route: ClassVar[str] = "/result"
    TITLE: ClassVar[str] = "RESULT"
    TITLE_SIZE: ClassVar[int] = Theme.TITLE_SIZE
    SPACING: ClassVar[int] = Theme.SPACING
    PADDING: ClassVar[int] = Theme.PAGE_PADDING

    def __init__(self, ctx: Any, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.reports: list[SessionReport] = []
        self.cards: list[ResultCard] = []
        self.body: ft.Column | None = None

    def _create_styled_button(
        self,
        text: str,
        width: int = 220,
    ) -> ft.Container:
        button_text = ft.Text(
            text,
            color=TEXT_COLOR,
            font_family=FONT_PIXEL,
            size=16,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        container = ft.Container(
            content=button_text,
            width=width,
            padding=10,
            bgcolor=BG_NORMAL,
            border=ft.Border.all(3, BORDER_COLOR),
            border_radius=8,
            ink=True,
            alignment=ft.Alignment(0, 0),
            animate=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
        )

        def handle_hover(e: ft.ControlEvent) -> None:
            is_hovered = e.data == "true" or e.data is True
            container.bgcolor = BG_HOVER if is_hovered else BG_NORMAL
            container.update()

        def handle_click(e: ft.ControlEvent) -> None:
            self.return_to_lobby()

        container.on_hover = handle_hover
        container.on_click = handle_click
        return container

    def build(self) -> ft.Control:
        self.body = ft.Column(
            controls=self._content(),
            spacing=self.SPACING,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
        return ft.Stack(
            controls=[
                ft.Image(src=self.BACKGROUND_PATH, fit=ft.BoxFit.COVER, width=float("inf"), height=float("inf")),
                ft.Container(content=self.body, padding=self.PADDING, left=0, right=0, top=0, bottom=0),
            ],
            expand=True,
        )

    def on_enter(self) -> None:
        try:
            self.reports = self._load_reports()
            self.cards = [
                ResultCard(report=report, nickname=self.ctx.players.get_player(report.player_id).nickname)
                for report in self.reports
            ]
        except AppError as error:
            self.show_error(error)
            return
        self._render()

    def return_to_lobby(self) -> None:
        self.ctx.nav.go("/lobby")

    def _load_reports(self) -> list[SessionReport]:
        session_id = self.params.get("session_id")
        room_id = self.params.get("room_id")
        if session_id is not None:
            return [self.ctx.analytics.session_report(int(session_id))]
        if room_id is not None:
            return self.ctx.analytics.room_reports(int(room_id))
        return []

    def _content(self) -> list[ft.Control]:
        controls: list[ft.Control] = [ft.Text(self.TITLE, size=self.TITLE_SIZE, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)]
        controls.extend(card.control for card in self.cards)
        controls.append(self._create_styled_button("RETURN TO LOBBY", width=220))
        return controls

    def _render(self) -> None:
        if self.body is None:
            return
        self.body.controls = self._content()
        self.body.update()