from __future__ import annotations

from typing import Any
from datetime import datetime

from ..dto import RoomDTO, PlayerDTO
from .enums import RoomStatus, EggTier


class GroupRoom:
    def __init__(
        self,
        id: int,
        subject: str,
        member_ids: list[int],
        session_ids: list[int],
        started_at: datetime,
    ):
        self.id = id
        self.subject = subject
        self.member_ids = member_ids
        self.session_ids = session_ids
        self.started_at = started_at

        self.status = RoomStatus.RUNNING
        self.ended_at: datetime | None = None
        self.duration_sec = 0
        self.tier: EggTier | None = None

    def stop(
        self,
        ended_at: datetime,
        duration_sec: int,
        min_success_sec: int,
    ) -> RoomStatus:
        self.ended_at = ended_at
        self.duration_sec = duration_sec

        if self.duration_sec >= min_success_sec:
            self.status = RoomStatus.READY_TO_HATCH
        else:
            self.status = RoomStatus.FAILED

        return self.status

    def can_hatch(self) -> bool:
        return self.status == RoomStatus.READY_TO_HATCH

    def mark_hatched(self, tier: EggTier) -> None:
        self.tier = tier
        self.status = RoomStatus.HATCHED

    def to_dto(self, members: list[PlayerDTO]) -> RoomDTO:
        return RoomDTO(
            id=self.id,
            subject=self.subject,
            members=members,
            started_at=self.started_at.isoformat(),
            status=self.status,
            session_ids=self.session_ids,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "subject": self.subject,
            "member_ids": self.member_ids,
            "session_ids": self.session_ids,
            "started_at": self.started_at.isoformat(),
            "status": self.status.value,
            "ended_at": (
                self.ended_at.isoformat()
                if self.ended_at is not None
                else None
            ),
            "duration_sec": self.duration_sec,
            "tier": self.tier.value if self.tier is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        room = cls(
            id=data["id"],
            subject=data["subject"],
            member_ids=data["member_ids"],
            session_ids=data["session_ids"],
            started_at=datetime.fromisoformat(data["started_at"]),
        )

        room.status = RoomStatus(data["status"])

        if data["ended_at"] is not None:
            room.ended_at = datetime.fromisoformat(data["ended_at"])

        room.duration_sec = data["duration_sec"]

        if data["tier"] is not None:
            room.tier = EggTier(data["tier"])

        return room