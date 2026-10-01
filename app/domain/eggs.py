from abc import ABC, abstractmethod

from app.domain.enums import EggTier, Rarity
from app.domain.species import Species
from app.domain.gacha import GachaMachine
from app.dto import TierInfo


class Egg(ABC):
    tier: EggTier
    name_th: str = ""
    image_path: str = ""

    @abstractmethod
    def rarity_weights(self) -> dict[Rarity, int]:
        pass

    def to_tier_info(self) -> TierInfo:
        return TierInfo(
            tier=self.tier,
            name_th=self.name_th,
            rarity_weights=self.rarity_weights(),
            image_path=self.image_path,
        )

    def roll_species(
        self,
        pool: list[Species],
        gacha: GachaMachine,
    ) -> Species:
        rarity = gacha.pick_rarity(self.rarity_weights())
        return gacha.pick_species(pool, rarity)


class FreshmanEgg(Egg):
    tier = EggTier.FRESHMAN
    name_th = "Freshman Egg"
    image_path = "eggs/freshman_egg.png"

    def rarity_weights(self) -> dict[Rarity, int]:
        return {
            Rarity.COMMON: 70,
            Rarity.RARE: 25,
            Rarity.EPIC: 5,
            Rarity.LEGENDARY: 0,
        }


class SeniorEgg(Egg):
    tier = EggTier.SENIOR
    name_th = "Senior Egg"
    image_path = "eggs/senior_egg.png"

    def rarity_weights(self) -> dict[Rarity, int]:
        return {
            Rarity.COMMON: 40,
            Rarity.RARE: 40,
            Rarity.EPIC: 17,
            Rarity.LEGENDARY: 3,
        }


class ProfessorEgg(Egg):
    tier = EggTier.PROFESSOR
    name_th = "Professor Egg"
    image_path = "eggs/professor_egg.png"

    def rarity_weights(self) -> dict[Rarity, int]:
        return {
            Rarity.COMMON: 10,
            Rarity.RARE: 40,
            Rarity.EPIC: 35,
            Rarity.LEGENDARY: 15,
        }
