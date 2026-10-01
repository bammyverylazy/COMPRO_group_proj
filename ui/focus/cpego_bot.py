from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from app.domain.enums import EggTier
from app.dto import TierOdds


@dataclass(frozen=True)
class CpegoMessage:
    text: str
    kind: str = "info"


class CpegoBot:
    SECONDS_PER_MINUTE: ClassVar[int] = 60

    def __init__(self, brackets: list[TierOdds]) -> None:
        self.brackets: list[TierOdds] = brackets
        self._announced: set[int] = set()

    def greeting(self, subject: str) -> CpegoMessage:
        first_minutes: int = self.brackets[0].min_minutes
        text: str = f"Let's study {subject}! Read for {first_minutes} minutes to earn an egg."
        return CpegoMessage(text=text, kind="greeting")

    def check(self, elapsed_sec: int) -> CpegoMessage | None:
        reached: list[TierOdds] = [
            bracket
            for bracket in self.brackets
            if elapsed_sec >= bracket.min_minutes * self.SECONDS_PER_MINUTE
            and bracket.min_minutes not in self._announced
        ]
        if not reached:
            return None
        self._announced.update(bracket.min_minutes for bracket in reached)
        return self._milestone(reached[-1])

    def reset(self) -> None:
        self._announced.clear()

    def _milestone(self, bracket: TierOdds) -> CpegoMessage:
        professor_percent: int = bracket.weights.get(EggTier.PROFESSOR, 0)
        text: str = f"{bracket.min_minutes} minutes done! You now have a {professor_percent}% chance at a Professor egg."
        return CpegoMessage(text=text, kind="milestone")
