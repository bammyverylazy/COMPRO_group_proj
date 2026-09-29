from __future__ import annotations

from app.data.game_store import GameStore
from app.domain.enums import EggTier, Rarity
from app.domain.species import Species
from app.dto import DexEntry


class DexService:
    def __init__(self, store: GameStore) -> None:
        self.store = store

    def list_entries(self, player_id: int) -> list[DexEntry]:
        tier_order = list(EggTier)
        rarity_order = list(Rarity)
        species_list = sorted(
            self.store.species.list_all(),
            key=lambda species: (tier_order.index(species.tier), rarity_order.index(species.rarity), species.code),
        )
        return [self._entry_for(player_id, species) for species in species_list]

    def get_entry(self, player_id: int, species_code: str) -> DexEntry:
        return self._entry_for(player_id, self.store.species.get(species_code))

    def completion(self, player_id: int) -> float:
        total = len(self.store.species.list_all())
        if total == 0:
            return 0.0
        unlocked = sum(
            1
            for pet in self.store.pets.list_by_player(player_id)
            if self.store.species.find(pet.species_code) is not None
        )
        return unlocked / total

    def _entry_for(self, player_id: int, species: Species) -> DexEntry:
        pet = self.store.pets.find_owned(player_id, species.code)
        if pet is None:
            return DexEntry(species=species.to_dto(), unlocked=False)
        return DexEntry(
            species=species.to_dto(),
            unlocked=True,
            level=pet.level,
            times_hatched=pet.times_hatched,
            first_hatched_at=pet.hatched_at,
            subjects=self._subjects_for(player_id, species.code),
        )

    def _subjects_for(self, player_id: int, species_code: str) -> list[str]:
        subjects: list[str] = []
        for session in self.store.sessions.list_by_player(player_id):
            if session.species_code == species_code and session.subject not in subjects:
                subjects.append(session.subject)
        return subjects
