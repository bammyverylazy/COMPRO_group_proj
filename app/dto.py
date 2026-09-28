from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import EggTier, Rarity, RoomStatus, SessionStatus


@dataclass
class PlayerDTO:
    id: int
    nickname: str

    def __str__(self):
        return f"id : {self.id}, nickname : {self.nickname}"


@dataclass
class SpeciesDTO:
    code: str
    name: str
    tier: EggTier
    rarity: Rarity
    sprite_path: str
    description: str = ""


@dataclass
class TierInfo:
    tier: EggTier
    name_th: str
    rarity_weights: dict[Rarity, int]
    image_path: str


@dataclass
class TierOdds:
    min_minutes: int
    max_minutes: int | None
    weights: dict[EggTier, int]


@dataclass
class SessionDTO:
    id: int
    player_id: int
    subject: str
    started_at: str
    status: SessionStatus
    room_id: int | None


@dataclass
class StopResult:
    session_id: int
    status: SessionStatus
    duration_sec: int
    tier_odds: dict[EggTier, int]


@dataclass
class PetDTO:
    species: SpeciesDTO
    level: int
    scale: float


@dataclass
class HatchResult:
    session_id: int
    player_id: int
    tier: EggTier
    pet: PetDTO
    is_new: bool


@dataclass
class RoomDTO:
    id: int
    subject: str
    members: list[PlayerDTO]
    started_at: str
    status: RoomStatus
    session_ids: list[int]


@dataclass
class RoomStopResult:
    room_id: int
    status: RoomStatus
    duration_sec: int
    tier_odds: dict[EggTier, int]


@dataclass
class RoomHatchResult:
    room_id: int
    tier: EggTier
    results: list[HatchResult]


@dataclass
class DexEntry:
    species: SpeciesDTO
    unlocked: bool
    level: int = 0
    times_hatched: int = 0
    first_hatched_at: datetime | None = None
    subjects: list[str] = field(default_factory=list)


@dataclass
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


@dataclass
class HistoryStats:
    total_sessions: int
    success_count: int
    fail_count: int
    success_rate: float
    total_study_sec: int
    tier_counts: dict[EggTier, int]
    subject_study_sec: dict[str, int]
    daily_study_sec: dict[str, int]


@dataclass
class History:
    reports: list[SessionReport]
    stats: HistoryStats