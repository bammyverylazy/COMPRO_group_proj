# มันติดกับโค้ดเค้า กะเลยเขียนไว้ แก้ได้เรย (แบมแบม)

class PetLevelPolicy:
    SCALE_STEP: float = 0.15
    MAX_SCALE: float = 2.0
    MAX_LEVEL: int = 99

    def next_level(self, level: int) -> int:
        return min(level + 1, self.MAX_LEVEL)

    def scale_for(self, level: int) -> float:
        return min(
            1 + (level - 1) * self.SCALE_STEP,
            self.MAX_SCALE
        )