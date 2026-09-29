from app.domain.enums import EggTier
from app.domain.tier_odds import TierOdds


class TierOddsTable:
    def __init__(self):
        self._brackets = [
            TierOdds(
                15,
                29,
                {
                    EggTier.FRESHMAN: 85,
                    EggTier.SENIOR: 13,
                    EggTier.PROFESSOR: 2,
                },
            ),
            TierOdds(
                30,
                59,
                {
                    EggTier.FRESHMAN: 55,
                    EggTier.SENIOR: 35,
                    EggTier.PROFESSOR: 10,
                },
            ),
            TierOdds(
                60,
                89,
                {
                    EggTier.FRESHMAN: 30,
                    EggTier.SENIOR: 45,
                    EggTier.PROFESSOR: 25,
                },
            ),
            TierOdds(
                90,
                None,
                {
                    EggTier.FRESHMAN: 15,
                    EggTier.SENIOR: 45,
                    EggTier.PROFESSOR: 40,
                },
            ),
        ]
        
    def bracket_for(self, duration_sec) -> TierOdds | None:
        duration_minutes = duration_sec // 60

        for bracket in self._brackets:
            if bracket.max_minutes is None:
                if duration_minutes >= bracket.min_minutes:
                    return bracket
            elif bracket.min_minutes <= duration_minutes <= bracket.max_minutes:
                return bracket

        return None
    
    def odds_for(self, duration_sec) -> dict[EggTier, int]:
        bracket = self.bracket_for(duration_sec)

        if bracket is None:
            return {}

        return bracket.weights
    
    def next_bracket(self, duration_sec) -> TierOdds | None:
        bracket = self.bracket_for(duration_sec)

        if bracket is None:
            return self._brackets[0]

        index = self._brackets.index(bracket)
        return self._brackets[index + 1] if index + 1 < len(self._brackets) else None
    
    def all_brackets(self) -> list[TierOdds]:
        return self._brackets