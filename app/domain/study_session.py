from __future__ import annotations

from typing import Any
from datetime import datetime, timezone

from ..services.app.dto import SessionDTO
from ..core.clock import Clock
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

    def stop(
        self,
        ended_at: datetime,
        min_success_sec: int,
    ):
        clock = Clock()

        self.ended_at = ended_at

        self.duration_sec = clock.elapsed_sec(
            self.started_at,
            self.ended_at,
        )

        if self.duration_sec >= min_success_sec:
            self.status = SessionStatus.READY_TO_HATCH
        else:
            self.status = SessionStatus.FAILED

    def can_hatch(self):
        return self.status == SessionStatus.READY_TO_HATCH

    def mark_hatched(self, tier: EggTier, species_code: str):
        self.tier = tier
        self.species_code = species_code
        self.status = SessionStatus.HATCHED

    def is_running(self):
        return self.status == SessionStatus.RUNNING

    def is_success(self):
        return self.status == SessionStatus.HATCHED

    def to_dto(self):
        return SessionDTO(
            id=self.id,
            player_id=self.player_id,
            subject=self.subject,
            started_at=self.started_at.isoformat(),
            status=self.status,
            room_id=self.room_id,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "subject": self.subject,
            "started_at": self.started_at.isoformat(),
            "status": self.status.value,
            "room_id": self.room_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            id=data["id"],
            player_id=data["player_id"],
            subject=data["subject"],
            started_at=datetime.fromisoformat(data["started_at"]),
            room_id=data["room_id"],
        )