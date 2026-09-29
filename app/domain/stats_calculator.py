from __future__ import annotations
from datetime import date, timedelta
from typing import ClassVar
from app.domain.enums import EggTier
from app.dto import HistoryStats, SessionReport

class StatsCalculator:
    DAYS_IN_CHART: ClassVar[int] = 7

    def compute(self, reports: list[SessionReport], today: date) -> HistoryStats:
        total_sessions = len(reports)
        total_study_sec = sum(r.duration_sec for r in reports)
        success_rate_val = self.success_rate(reports)
        tiers = self.tier_counts(reports)
        subjects = self.subject_study_sec(reports)
        daily = self.daily_study_sec(reports, today)
        
        return HistoryStats(
            total_sessions=total_sessions,
            total_study_sec=total_study_sec,
            success_rate=success_rate_val,
            tier_counts=tiers,
            subject_study_sec=subjects,
            daily_study_sec=daily
        )
    def success_rate(self, reports: list[SessionReport]) -> float:
        if not reports:
            return 0.0
        success_count = sum(1 for r in reports if r.is_success)
        return success_count / len(reports)
    def tier_counts(self, reports: list[SessionReport]) -> dict[EggTier, int]:
        counts = {tier: 0 for tier in EggTier}
        for r in reports:
            if r.tier in counts:
                counts[r.tier] += 1
        return counts
    def subject_study_sec(self, reports: list[SessionReport]) -> dict[str, int]:
        stats: dict[str, int] = {}
        for r in reports:
            stats[r.subject] = stats.get(r.subject, 0) + r.duration_sec
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
    def daily_study_sec(self, reports: list[SessionReport], today: date) -> dict[str, int]:
        daily_map = {}
        for i in range(self.DAYS_IN_CHART - 1, -1, -1):
            d = today - timedelta(days=i)
            daily_map[d.isoformat()] = 0
            
        for r in reports:
            date_str = r.ended_at.date().isoformat() if hasattr(r, 'ended_at') else None
            if date_str in daily_map:
                daily_map[date_str] += r.duration_sec
        return daily_map