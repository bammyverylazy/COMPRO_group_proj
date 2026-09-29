from app.domain.egg_factory import EggFactory
from app.domain.tier_odds_table import TierOddsTable


class TierService:
    def __init__(self):
        self.factory = EggFactory()
        self.odds_table = TierOddsTable()
        
    def list_tiers(self):
        eggs = self.factory.all()
        return [egg.to_tier_info() for egg in eggs]
    
    def list_odds(self):
        return self.odds_table.all_brackets()
    
    def odds_for(self, duration_sec: int):
        return self.odds_table.odds_for(duration_sec)
    
    def next_bracket(self, duration_sec: int):
        return self.odds_table.next_bracket(duration_sec)