from __future__ import annotations
from ..services.dto import SpeciesDTO
from .enums import EggTier,Rarity
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..dto import SpeciesDTO
from .enums import EggTier, Rarity


@dataclass
class Species:
    code: str
    name: str
    tier: EggTier
    rarity: Rarity
    sprite_path: str
    description: str = ""

    def to_dto(self) -> SpeciesDTO:
        return SpeciesDTO(
            code=self.code,
            name=self.name,
            tier=self.tier,
            rarity=self.rarity,
            sprite_path=self.sprite_path,
            description=self.description,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "tier": self.tier.value,
            "rarity": self.rarity.value,
            "sprite_path": self.sprite_path,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Species":
        return cls(
            code=data["code"],
            name=data["name"],
            tier=EggTier(data["tier"]),
            rarity=Rarity(data["rarity"]),
            sprite_path=data["sprite_path"],
            description=data.get("description", ""),
        )