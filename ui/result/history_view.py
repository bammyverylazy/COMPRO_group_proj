from __future__ import annotations

from datetime import date
from typing import Any, ClassVar

import flet as ft

from app.dto import History, SessionReport
from ui.core.base_view import BaseView
from ui.core.format import Format
from ui.core.widgets import StatTile
from ui.result.bar_chart import BarChart


class HistoryView(BaseView):
    route: ClassVar[str] = "/history"

    def __init__(self, ctx: Any, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.history: History | None = None
        self.daily_chart: BarChart | None = None
        self.subject_chart: BarChart | None = None

    def build(self) -> ft.Control:
        if self.history is None:
            return ft.Column([ft.Text("No history")])

        stats = self.history.stats
        stat_tiles = [
            StatTile("รอบทั้งหมด", str(stats.total_sessions)).control,
            StatTile("อัตราสำเร็จ", f"{stats.success_rate:.1%}").control,
            StatTile("เวลารวม", Format.duration(stats.total_study_sec)).control,
        ]

        controls: list[ft.Control] = [
            ft.Row(stat_tiles, wrap=True),
        ]

        if self.daily_chart is not None:
            controls.append(ft.Text("7 วัน"))
            controls.append(self.daily_chart.build())
        if self.subject_chart is not None:
            controls.append(ft.Text("แยกวิชา"))
            controls.append(self.subject_chart.build())

        for report in self.history.reports:
            controls.append(self.render_row(report))

        return ft.Column(controls, spacing=12, scroll=ft.ScrollMode.AUTO)

    def on_enter(self) -> None:
        if self.ctx.player is None:
            return
        self.history = self.ctx.analytics.history(self.ctx.player.id)
        daily_values = dict(self.history.stats.daily_study_sec)
        subject_values = dict(self.history.stats.subject_study_sec)
        self.daily_chart = BarChart(daily_values, lambda value: Format.duration(value), 140)
        self.subject_chart = BarChart(subject_values, lambda value: f"{value // 60}m", 140)

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
            border=ft.border.all(1, ft.Colors.GREY_300),
            padding=8,
            border_radius=8,
        )

    def open_report(self, session_id: int) -> None:
        self.ctx.nav.go("/result", session_id=session_id)

    def close(self) -> None:
        self.ctx.nav.go("/lobby")
