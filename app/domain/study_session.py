from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..dto import SessionDTO
from .enums import EggTier, SessionStatus


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
        duration_sec: int,
        min_success_sec: int,
    ):
        self.ended_at = ended_at
        self.duration_sec = duration_sec

        if self.duration_sec >= min_success_sec:
            self.status = SessionStatus.READY_TO_HATCH
        else:
            self.status = SessionStatus.FAILED

        return self.status

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
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_sec": self.duration_sec,
            "tier": self.tier.value if self.tier else None,
            "species_code": self.species_code,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        session = cls(
            id=data["id"],
            player_id=data["player_id"],
            subject=data["subject"],
            started_at=datetime.fromisoformat(data["started_at"]),
            room_id=data.get("room_id"),
        )

        session.status = SessionStatus(data["status"])
        session.ended_at = (
            datetime.fromisoformat(data["ended_at"])
            if data.get("ended_at") is not None
            else None
        )
        session.duration_sec = data.get("duration_sec", 0)
        session.tier = EggTier(data["tier"]) if data.get("tier") is not None else None
        session.species_code = data.get("species_code")
        return session