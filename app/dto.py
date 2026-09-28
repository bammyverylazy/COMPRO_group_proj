from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from domain.enums import EggTier, Rarity, SessionStatus, RoomStatus


@dataclass(frozen=True)
class PlayerDTO:
    id: int
    nickname: str
    
    def __str__(self):
        return f"id : {self.id}, nickname : {self.nickname}"


@dataclass(frozen=True)
class SpeciesDTO:
    code: str
    name: str
    tier: EggTier
    rarity: Rarity
    sprite_path: str
    description: str


@dataclass(frozen=True)
class TierInfo:
    tier: EggTier
    name_th: str
    rarity_weights: dict[Rarity, int]
    image_path: str


@dataclass(frozen=True)
class TierOdds:
    min_minutes: int
    max_minutes: int | None
    weights: dict[EggTier, int]


@dataclass(frozen=True)
class SessionDTO:
    id: int
    player_id: int
    subject: str
    started_at: str
    status: SessionStatus
    room_id: int | None


@dataclass(frozen=True)
class StopResult:
    session_id: int
    status: SessionStatus
    duration_sec: int
    tier_odds: dict[EggTier, int]


@dataclass(frozen=True)
class PetDTO:
    species: SpeciesDTO
    level: int
    scale: float


@dataclass(frozen=True)
class HatchResult:
    session_id: int
    player_id: int
    tier: EggTier
    pet: PetDTO
    is_new: bool


@dataclass(frozen=True)
class RoomDTO:
    id: int
    subject: str
    members: list[PlayerDTO]
    started_at: datetime
    status: RoomStatus
    session_ids: list[int]


@dataclass(frozen=True)
class RoomStopResult:
    room_id: int
    status: RoomStatus
    duration_sec: int
    tier_odds: dict[EggTier, int]


@dataclass(frozen=True)
class RoomHatchResult:
    room_id: int
    tier: EggTier
    results: list[HatchResult]


@dataclass(frozen=True)
class DexEntry:
    species: SpeciesDTO
    unlocked: bool
    level: int = 0
    times_hatched: int = 0
    first_hatched_at: datetime | None = None
    subjects: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SessionReport:
    session_id: int
    player_id: int
    subject: str
    status: SessionStatus
    is_success: bool
    duration_sec: int
    started_at: datetime
    ended_at: datetime | None
    remaining_sec: int = 0
    tier: EggTier | None = None
    pet: PetDTO | None = None
    is_new: bool | None = None
    room_id: int | None = None


@dataclass(frozen=True)
class HistoryStats:
    total_sessions: int
    success_count: int
    fail_count: int
    success_rate: float
    total_study_sec: int
    tier_counts: dict[EggTier, int]
    subject_study_sec: dict[str, int]
    daily_study_sec: dict[str, int]


@dataclass(frozen=True)
class History:
    reports: list[SessionReport]
    stats: HistoryStats