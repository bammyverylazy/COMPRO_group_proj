from typing import List
from app.domain.enums import EggTier


class DexService:
    def __init__(self, store):
        self.store = store
    def list_entries(self, player_id: int):
        entries = self.store.get_dex_entries(player_id)
        tier_order = {
            EggTier.FRESHMAN: 1,
            EggTier.SENIOR: 2,
            EggTier.PROFESSOR: 3,
        }
        
        def get_sort_key(entry):
            tier_val = tier_order.get(entry.species.tier, 99)
            rarity_val = getattr(entry.species, 'rarity', 0)
            return (tier_val, rarity_val)

        return sorted(entries, key=get_sort_key)

    def get_entry(self, player_id: int, species_code: str):
        return self.store.get_dex_entry_detail(player_id, species_code)

    def completion(self, player_id: int) -> float:
        entries = self.store.get_dex_entries(player_id)
        if not entries:
            return 0.0
        
        unlocked_count = sum(1 for entry in entries if entry.is_unlocked)
        total_count = len(entries)
        
        return unlocked_count / total_count