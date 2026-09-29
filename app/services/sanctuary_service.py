from __future__ import annotations

from app.data.game_store import GameStore
from app.domain.pet_policy import PetLevelPolicy
from app.dto import PetDTO


class SanctuaryService:
    def __init__(self, store: GameStore) -> None:
        self.store = store
        self.policy = PetLevelPolicy()

    def list_pets(self, player_id: int) -> list[PetDTO]:
        return [
            pet.to_dto(self.store.species.get(pet.species_code), self.policy)
            for pet in self.store.pets.list_by_player(player_id)
        ]

    def count_pets(self, player_id: int) -> int:
        return len(self.store.pets.list_by_player(player_id))
