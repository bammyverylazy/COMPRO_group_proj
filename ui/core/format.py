from __future__ import annotations
from app.domain.enums import EggTier

_TIER_NAMES_TH: dict[EggTier, str] = {
    EggTier.FRESHMAN: "Freshman Egg",
    EggTier.SENIOR: "Senior Egg",
    EggTier.PROFESSOR: "Professor Egg",
}


class Format:
    @staticmethod
    def clock(seconds: int) -> str:
        minutes, secs = divmod(seconds, 60)
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def duration(seconds: int) -> str:
        hours, remainder = divmod(seconds, 3600)
        minutes = remainder // 60
        if hours > 0:
            return f"{hours} h {minutes} min"
        return f"{minutes} min"

    @staticmethod
    def percent(value: float) -> str:
        return f"{value * 100:.1f}%"

    @staticmethod
    def tier_name(tier: EggTier) -> str:
        return _TIER_NAMES_TH[tier]

