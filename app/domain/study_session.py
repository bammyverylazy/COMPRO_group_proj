from __future__ import annotations

from datetime import datetime, timezone

from .enums import SessionStatus, EggTier


class StudySession:
    def __init__(
        self,
        id: int,
        player_id: int,
        subject: str,
        started_at: datetime | None = None,
        room_id: int | None = None,
    ):
        self.id = id
        self.player_id = player_id
        self.subject = subject

        if started_at is None:
            started_at = datetime.now(timezone.utc)

        self.started_at = started_at
        self.room_id = room_id

        self.status = SessionStatus.RUNNING
        self.ended_at: datetime | None = None
        self.duration_sec = 0
        self.tier: EggTier | None = None
        self.species_code: str | None = None