import random
from typing import Any

from app.domain.enums import EggTier, Rarity
from app.domain.species import Species


class GachaMachine:
    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def pick_weighted(self, weights: dict[Any, int]) -> Any:
        if not weights:
            raise ValueError("weights cannot be empty")

        if any(weight < 0 for weight in weights.values()):
            raise ValueError("weights cannot contain negative values")

        total = sum(weights.values())

        if total <= 0:
            raise ValueError("weights must have a positive total")

        roll = self.rng.uniform(0, total)

        for key, weight in weights.items():
            if weight == 0:
                continue

            roll -= weight

            if roll < 0:
                return key

        raise RuntimeError("failed to pick a weighted item")

    def pick_tier(self, weights: dict[EggTier, int]) -> EggTier:
        return self.pick_weighted(weights)

    def pick_rarity(self, weights: dict[Rarity, int]) -> Rarity:
        return self.pick_weighted(weights)

    def pick_species(
        self,
        pool: list[Species],
        rarity: Rarity,
    ) -> Species:
        rarities = [
            Rarity.COMMON,
            Rarity.RARE,
            Rarity.EPIC,
            Rarity.LEGENDARY,
        ]

        while True:
            candidates = [
                species
                for species in pool
                if species.rarity is rarity
            ]

            if candidates:
                return self.rng.choice(candidates)

            index = rarities.index(rarity)

            if index > 0:
                rarity = rarities[index - 1]
            else:
                raise ValueError("no species available")