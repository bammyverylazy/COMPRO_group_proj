from __future__ import annotations

from datetime import date
from typing import Any, ClassVar

import flet as ft

from app.domain.enums import EggTier
from app.dto import History, SessionReport
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.format import Format
from ui.core.theme import Theme
from ui.core.widgets import PixelButton, StatTile
from ui.result.bar_chart import BarChart


class HistoryView(BaseView):
    BACKGROUND_PATH: ClassVar[str] = "backgrounds/result_background.png"
    route: ClassVar[str] = "/history"
    TITLE: ClassVar[str] = "HISTORY"
    TITLE_SIZE: ClassVar[int] = Theme.TITLE_SIZE
    EMPTY_TEXT: ClassVar[str] = "No study history yet. Press START in the lobby to begin!"
    PANEL_COLOR: ClassVar[str] = Theme.PANEL_COLOR
    CHART_HEIGHT: ClassVar[int] = 120
    SPACING: ClassVar[int] = Theme.SPACING
    PADDING: ClassVar[int] = Theme.PAGE_PADDING
    EGG_IMAGES: ClassVar[dict[EggTier, str]] = {
        EggTier.FRESHMAN: "eggs/freshman_egg.png",
        EggTier.SENIOR: "eggs/senior_egg.png",
        EggTier.PROFESSOR: "eggs/professor_egg.png",
    }

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
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
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
        if self.ctx.player is None:
            return
        try:
            self.history = self.ctx.analytics.history(self.ctx.player.id)
        except AppError as error:
            self.show_error(error)
            return
        stats = self.history.stats
        daily = {self._short_date(day): seconds for day, seconds in stats.daily_study_sec.items()}
        self.daily_chart = BarChart(daily, self._short_minutes, self.CHART_HEIGHT)
        self.subject_chart = BarChart(dict(stats.subject_study_sec), self._short_minutes, self.CHART_HEIGHT)
        self._render()

    def render_row(self, report: SessionReport) -> ft.Control:
        moment = report.ended_at or report.started_at
        date_text = moment.astimezone().strftime("%d/%m") if moment is not None else date.today().strftime("%d/%m")
        result_text = "Hatched" if report.is_success else "Failed"
        result_color = Theme.ACCENT if report.is_success else "white70"
        leading: ft.Control = ft.Container(width=28)
        if report.tier is not None:
            leading = ft.Image(src=self.EGG_IMAGES[report.tier], width=28, height=28, fit=ft.BoxFit.CONTAIN)
        row = ft.Row(
            controls=[
                leading,
                ft.Text(date_text, width=44, color=ft.Colors.WHITE, size=13),
                ft.Text(report.subject, expand=True, color=ft.Colors.WHITE, size=13, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(self._short_minutes(report.duration_sec), width=56, color=ft.Colors.WHITE, size=13),
                ft.Text(result_text, width=64, color=result_color, size=13, weight=ft.FontWeight.BOLD),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        row_container = ft.Container(
            content=row,
            bgcolor=self.PANEL_COLOR,
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=10,
            on_click=lambda event, session_id=report.session_id: self.open_report(session_id),
        )
        return self.ctx.sound.bind_button(row_container)

    def open_report(self, session_id: int) -> None:
        self.ctx.nav.go("/result", session_id=session_id)

    def close(self) -> None:
        self.ctx.nav.go("/lobby")

    def _content(self) -> list[ft.Control]:
        header = ft.Row(
            controls=[
                ft.Text(self.TITLE, size=self.TITLE_SIZE, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                PixelButton(
                    "BACK",
                    on_click=self.close,
                    variant="secondary",
                    sound=self.ctx.sound,
                ).control,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        controls: list[ft.Control] = [header]
        if self.history is None or not self.history.reports:
            controls.append(self._panel([ft.Text(self.EMPTY_TEXT, color=ft.Colors.WHITE)]))
            return controls
        controls.extend(self._stats_section(self.history))
        return controls

    def _stats_section(self, history: History) -> list[ft.Control]:
        stats = history.stats
        stat_tiles = [
            StatTile("Sessions", str(stats.total_sessions)).control,
            StatTile("Success rate", f"{stats.success_rate:.0%}").control,
            StatTile("Total time", Format.duration(stats.total_study_sec)).control,
        ]
        egg_row = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Image(src=self.EGG_IMAGES[tier], width=32, height=32, fit=ft.BoxFit.CONTAIN),
                        ft.Text(f"× {stats.tier_counts.get(tier, 0)}", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=4,
                )
                for tier in self.EGG_IMAGES
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )
        controls: list[ft.Control] = [
            ft.Row(stat_tiles, wrap=True, alignment=ft.MainAxisAlignment.CENTER),
            self._panel([self._section_title("Eggs hatched"), egg_row]),
        ]
        if self.daily_chart is not None:
            controls.append(self._panel([self._section_title("Last 7 days"), self.daily_chart.control]))
        if self.subject_chart is not None:
            controls.append(self._panel([self._section_title("By subject"), self.subject_chart.control]))
        controls.append(self._section_title("All sessions (tap to view)"))
        controls.extend(self.render_row(report) for report in history.reports)
        return controls

    def _panel(self, controls: list[ft.Control]) -> ft.Control:
        return ft.Container(
            content=ft.Column(controls, spacing=8, tight=True),
            bgcolor=self.PANEL_COLOR,
            border_radius=Theme.PANEL_RADIUS,
            padding=Theme.PANEL_PADDING,
        )

    def _section_title(self, text: str) -> ft.Control:
        return ft.Text(text, size=Theme.HEADING_SIZE, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

    def _short_date(self, iso_day: str) -> str:
        return date.fromisoformat(iso_day).strftime("%d/%m")

    def _short_minutes(self, seconds: int) -> str:
        return f"{seconds // 60}m"

    def _render(self) -> None:
        if self.body is None:
            return
        self.body.controls = self._content()
        self.body.update()
