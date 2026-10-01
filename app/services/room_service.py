from __future__ import annotations

from app.config import Settings
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.domain.enums import RoomStatus
from app.domain.group_room import GroupRoom
from app.domain.study_session import StudySession
from app.domain.tier_odds_table import TierOddsTable
from app.dto import RoomDTO, RoomHatchResult, RoomStopResult
from app.errors import InvalidStateError, ValidationError
from app.services.hatch_service import HatchService


class RoomService:
    def __init__(self, store: GameStore, clock: Clock, settings: Settings, hatch_service: HatchService) -> None:
        self.store = store
        self.clock = clock
        self.settings = settings
        self.hatch_service = hatch_service
        self.odds_table = TierOddsTable()

    def create_room(self, member_ids: list[int], subject: str) -> RoomDTO:
        clean_subject = subject.strip()
        if not clean_subject:
            raise ValidationError("Please enter a subject", field="subject")
        self._validate_members(member_ids)
        started_at = self.clock.now()
        session_ids: list[int] = []
        room_id = self.store.rooms.next_id()
        for player_id in member_ids:
            session = StudySession(
                id=self.store.sessions.next_id(),
                player_id=player_id,
                subject=clean_subject,
                started_at=started_at,
                room_id=room_id,
            )
            self.store.sessions.add(session)
            session_ids.append(session.id)
        room = GroupRoom(
            id=room_id,
            subject=clean_subject,
            member_ids=list(member_ids),
            session_ids=session_ids,
            started_at=started_at,
        )
        self.store.rooms.add(room)
        self.store.save()
        return self._to_dto(room)

    def get_room(self, room_id: int) -> RoomDTO:
        return self._to_dto(self.store.rooms.get(room_id))

    def elapsed(self, room_id: int) -> int:
        room = self.store.rooms.get(room_id)
        if room.ended_at is not None:
            return room.duration_sec
        return self.clock.elapsed_sec(room.started_at)

    def stop(self, room_id: int) -> RoomStopResult:
        room = self.store.rooms.get(room_id)
        if room.status is not RoomStatus.RUNNING:
            raise InvalidStateError("This room has already stopped")
        ended_at = self.clock.now()
        duration_sec = self.clock.elapsed_sec(room.started_at)
        min_success_sec = self._min_success_sec()
        status = room.stop(ended_at, duration_sec, min_success_sec)
        for session_id in room.session_ids:
            session = self.store.sessions.get(session_id)
            if session.is_running():
                session.stop(ended_at, duration_sec, min_success_sec)
        self.store.save()
        tier_odds = self.odds_table.odds_for(duration_sec) if status is RoomStatus.READY_TO_HATCH else {}
        return RoomStopResult(
            room_id=room.id,
            status=status,
            duration_sec=duration_sec,
            tier_odds=dict(tier_odds),
        )

    def hatch(self, room_id: int) -> RoomHatchResult:
        room = self.store.rooms.get(room_id)
        if not room.can_hatch():
            raise InvalidStateError("This room is not ready to hatch")
        tier = self.hatch_service.roll_tier(room.duration_sec)
        results = [self.hatch_service.hatch(session_id, tier) for session_id in room.session_ids]
        room.mark_hatched(tier)
        self.store.save()
        return RoomHatchResult(room_id=room.id, tier=tier, results=results)

    def _validate_members(self, member_ids: list[int]) -> None:
        count = len(member_ids)
        if count < self.settings.min_room_members or count > self.settings.max_room_members:
            raise ValidationError(
                f"A room needs {self.settings.min_room_members}-{self.settings.max_room_members} members",
                field="member_ids",
            )
        if len(set(member_ids)) != count:
            raise ValidationError("A member was selected twice", field="member_ids")
        for player_id in member_ids:
            player = self.store.players.get(player_id)
            if self.store.sessions.get_running(player_id) is not None:
                raise InvalidStateError(f"{player.nickname} already has a session in progress")

    def _to_dto(self, room: GroupRoom) -> RoomDTO:
        members = [self.store.players.get(player_id).to_dto() for player_id in room.member_ids]
        return room.to_dto(members)

    def _min_success_sec(self) -> int:
        return self.settings.min_success_minutes * 60
