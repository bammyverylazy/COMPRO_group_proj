from app.domain.egg_factory import EggFactory
from app.domain.enums import EggTier
from app.domain.tier_odds import TierOdds
from app.domain.tier_odds_table import TierOddsTable
from app.dto import TierInfo


class TierService:
    def __init__(self):
        self.factory = EggFactory()
        self.odds_table = TierOddsTable()

    def list_tiers(self) -> list[TierInfo]:
        eggs = self.factory.all()
        return [egg.to_tier_info() for egg in eggs]

    def list_odds(self) -> list[TierOdds]:
        return self.odds_table.all_brackets()

    def odds_for(self, duration_sec: int) -> dict[EggTier, int]:
        return self.odds_table.odds_for(duration_sec)

    def next_bracket(self, duration_sec: int) -> TierOdds | None:
        return self.odds_table.next_bracket(duration_sec)