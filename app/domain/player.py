from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..dto import PlayerDTO


class Player:
    def __init__(self, id: int, nickname: str, created_at: datetime | None = None):
        self.id = id
        self.nickname = nickname
        if created_at is None:
            created_at = datetime.now(timezone.utc)
        self.created_at = created_at

    def to_dto(self) -> PlayerDTO:
        return PlayerDTO(id=self.id, nickname=self.nickname)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nickname": self.nickname,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Player":
        return cls(
            id=data["id"],
            nickname=data["nickname"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )