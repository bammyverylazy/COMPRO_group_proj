from __future__ import annotations
from ..dto import PlayerDTO
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar
import json

class Player:
    def __init__(self, id:int, nickname:str, created_at = None):
        self.id = id
        self.nickname = nickname
        if created_at is None:
            created_at = datetime.now(timezone.utc) 
        self.created_at = created_at
        
    def to_dto(self): # Player → PlayerDTO
        return  PlayerDTO(
    id=self.id,
    nickname=self.nickname
) 
        #return PlayerDTO
    def to_dict(self): # Player → dict
        return {
    "id": self.id,
    "nickname": self.nickname,
    "created_at": self.created_at.isoformat() # to str
}
        
    @classmethod
    def from_dict(cls, data: dict[str, Any]): # dict → Player
        return cls(data["id"], data["nickname"], datetime.fromisoformat(data["created_at"]))