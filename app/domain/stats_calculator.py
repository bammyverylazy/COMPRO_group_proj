from __future__ import annotations

from datetime import date, timedelta
from typing import ClassVar

from app.domain.enums import EggTier
from app.dto import HistoryStats, SessionReport


class StatsCalculator:
    DAYS_IN_CHART: ClassVar[int] = 7

    def compute(self, reports: list[SessionReport], today: date) -> HistoryStats:
        success_count = sum(1 for report in reports if report.is_success)
        return HistoryStats(
            total_sessions=len(reports),
            success_count=success_count,
            fail_count=len(reports) - success_count,
            success_rate=self.success_rate(reports),
            total_study_sec=sum(report.duration_sec for report in reports),
            tier_counts=self.tier_counts(reports),
            subject_study_sec=self.subject_study_sec(reports),
            daily_study_sec=self.daily_study_sec(reports, today),
        )

    def success_rate(self, reports: list[SessionReport]) -> float:
        if not reports:
            return 0.0
        return sum(1 for report in reports if report.is_success) / len(reports)

    def tier_counts(self, reports: list[SessionReport]) -> dict[EggTier, int]:
        counts = {tier: 0 for tier in EggTier}
        for report in reports:
            if report.tier is not None:
                counts[report.tier] += 1
        return counts

    def subject_study_sec(self, reports: list[SessionReport]) -> dict[str, int]:
        totals: dict[str, int] = {}
        for report in reports:
            totals[report.subject] = totals.get(report.subject, 0) + report.duration_sec
        return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))

    def daily_study_sec(self, reports: list[SessionReport], today: date) -> dict[str, int]:
        days = [today - timedelta(days=offset) for offset in range(self.DAYS_IN_CHART - 1, -1, -1)]
        totals = {day.isoformat(): 0 for day in days}
        for report in reports:
            key = report.started_at.astimezone().date().isoformat()
            if key in totals:
                totals[key] += report.duration_sec
        return totals
