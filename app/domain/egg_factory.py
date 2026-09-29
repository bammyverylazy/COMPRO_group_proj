from app.domain.eggs import Egg, FreshmanEgg, SeniorEgg, ProfessorEgg
from app.domain.enums import EggTier

class EggFactory:
    def __init__(self):
        self._registry = {
            EggTier.FRESHMAN: FreshmanEgg,
            EggTier.SENIOR: SeniorEgg,
            EggTier.PROFESSOR: ProfessorEgg
        }
    
    def create(self, tier: EggTier) -> Egg:
        egg_class = self._registry[tier]
        return egg_class()
    
    def all(self) -> list[Egg]:
        return [egg_class() for egg_class in self._registry.values()]


