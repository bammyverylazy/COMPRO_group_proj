from __future__ import annotations
from app.domain.pet_policy import PetLevelPolicy
from app.dto import PetDTO

class SanctuaryService:
    def __init__(self, store: GameStore):
        self.store = store
        self.policy = PetLevelPolicy()

    def list_pets(self, player_id: int) -> list[PetDTO]:
        pets = self.store.get_owned_pets(player_id)

        result: list[PetDTO] = []

        for pet in pets:
            result.append(
                pet.to_dto(level=self.policy.level_for(pet),scale=self.policy.scale_for(pet))
            )

        return result

    def count_pets(self, player_id: int) -> int:
        pets = self.store.get_owned_pets(player_id)

        return len(pets)