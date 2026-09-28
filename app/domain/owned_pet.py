from __future__ import annotations

from typing import Any
from datetime import datetime

from ..dto import PetDTO
from .species import Species
from .pet_policy import PetLevelPolicy


class OwnedPet:
    def __init__(
        self,
        player_id: int,
        species_code: str,
        hatched_at: datetime,
        level: int = 1,
        times_hatched: int = 1,
    ):
        self.player_id = player_id
        self.species_code = species_code
        self.hatched_at = hatched_at
        self.level = level
        self.times_hatched = times_hatched

    def level_up(self, policy: PetLevelPolicy):
        self.times_hatched += 1
        self.level = policy.next_level(self.level)

    def scale(self, policy: PetLevelPolicy):
        return policy.scale_for(self.level)

    def to_dto(self, species: Species, policy: PetLevelPolicy):
        return PetDTO(
            species=species.to_dto(),
            level=self.level,
            scale=policy.scale_for(self.level),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "player_id": self.player_id,
            "species_code": self.species_code,
            "hatched_at": self.hatched_at.isoformat(),
            "level": self.level,
            "times_hatched": self.times_hatched,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            player_id=data["player_id"],
            species_code=data["species_code"],
            hatched_at=datetime.fromisoformat(data["hatched_at"]),
            level=data["level"],
            times_hatched=data["times_hatched"],
        )