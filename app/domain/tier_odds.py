from app.domain.enums import EggTier

class TierOdds:
    def __init__(
        self,
        min_minutes: int,
        max_minutes: int | None,
        weights: dict[EggTier, int],
    ):
        self.min_minutes = min_minutes
        self.max_minutes = max_minutes
        self.weights = weights