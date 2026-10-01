from __future__ import annotations

from datetime import date
from functools import partial
from typing import Any, ClassVar

import flet as ft

from app.dto import History, SessionReport
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.format import Format
from ui.core.widgets import PixelButton, StatTile
from ui.result.bar_chart import BarChart


class HistoryView(BaseView):
    route: ClassVar[str] = "/history"
    TITLE: ClassVar[str] = "HISTORY"
    TITLE_SIZE: ClassVar[int] = 28
    EMPTY_TEXT: ClassVar[str] = "No history yet"
    CHART_HEIGHT: ClassVar[int] = 140
    SPACING: ClassVar[int] = 12
    PADDING: ClassVar[int] = 16

    def __init__(self, ctx: Any, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.history: History | None = None
        self.daily_chart: BarChart | None = None
        self.subject_chart: BarChart | None = None
        self.body: ft.Column | None = None

    def build(self) -> ft.Control:
        self.body = ft.Column(
            controls=self._content(),
            spacing=self.SPACING,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        return ft.Container(content=self.body, padding=self.PADDING, expand=True)

    def on_enter(self) -> None:
        if self.ctx.player is None:
            return
        try:
            self.history = self.ctx.analytics.history(self.ctx.player.id)
        except AppError as error:
            self.show_error(error)
            return
        stats = self.history.stats
        self.daily_chart = BarChart(dict(stats.daily_study_sec), Format.duration, self.CHART_HEIGHT)
        self.subject_chart = BarChart(
            dict(stats.subject_study_sec),
            lambda value: f"{value // 60}m",
            self.CHART_HEIGHT,
        )
        self._render()

    def render_row(self, report: SessionReport) -> ft.Control:
        date_text = report.ended_at.date().isoformat() if report.ended_at is not None else date.today().isoformat()
        result_text = "สำเร็จ" if report.is_success else "ยังไม่สำเร็จ"
        row = ft.Row(
            controls=[
                ft.Text(date_text, width=100),
                ft.Text(report.subject, width=120),
                ft.Text(Format.duration(report.duration_sec), width=90),
                ft.Text(result_text, width=90),
            ],
            spacing=12,
        )
        return ft.Container(
            content=row,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            padding=8,
            border_radius=8,
            on_click=partial(self._on_row_click, report.session_id),
        )

    def open_report(self, session_id: int) -> None:
        self.ctx.nav.go("/result", session_id=session_id)

    def close(self) -> None:
        self.ctx.nav.go("/lobby")

    def _on_row_click(self, session_id: int, event: ft.ControlEvent) -> None:
        self.open_report(session_id)

    def _content(self) -> list[ft.Control]:
        controls: list[ft.Control] = [
            ft.Text(self.TITLE, size=self.TITLE_SIZE, weight=ft.FontWeight.BOLD),
        ]
        if self.history is None or not self.history.reports:
            controls.append(ft.Text(self.EMPTY_TEXT))
        else:
            controls.extend(self._stats_section(self.history))
        controls.append(PixelButton("BACK", on_click=self.close, variant="secondary").control)
        return controls

    def _stats_section(self, history: History) -> list[ft.Control]:
        stats = history.stats
        stat_tiles = [
            StatTile("รอบทั้งหมด", str(stats.total_sessions)).control,
            StatTile("อัตราสำเร็จ", f"{stats.success_rate:.1%}").control,
            StatTile("เวลารวม", Format.duration(stats.total_study_sec)).control,
        ]
        controls: list[ft.Control] = [ft.Row(stat_tiles, wrap=True)]
        if self.daily_chart is not None:
            controls.append(ft.Text("7 วัน"))
            controls.append(self.daily_chart.control)
        if self.subject_chart is not None:
            controls.append(ft.Text("แยกวิชา"))
            controls.append(self.subject_chart.control)
        controls.extend(self.render_row(report) for report in history.reports)
        return controls

    def _render(self) -> None:
        if self.body is None:
            return
        self.body.controls = self._content()
        self.body.update()
