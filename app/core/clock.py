from __future__ import annotations

from datetime import datetime, timezone


class Clock:
    def __init__(self, speed: float = 1.0):
        self.speed = speed

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def elapsed_sec(self, started_at: datetime, until: datetime | None = None) -> int:
        if until is None:
            until = self.now()

        elapsed = (until - started_at).total_seconds() * self.speed
        return int(elapsed)

