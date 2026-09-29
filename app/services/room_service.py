from __future__ import annotations
from app.config import Settings
from app.core.clock import Clock

from app.domain.enums import RoomStatus
from app.domain.group_room import GroupRoom
from app.domain.tier_odds_table import TierOddsTable
from app.dto import RoomDTO, RoomHatchResult, RoomStopResult
from app.errors import InvalidStateError, NotFoundError, ValidationError
from app.services.hatch_service import HatchService


class RoomService:
    
    def __init__(self, store: GameStore, clock: Clock, settings: Settings, hatch_service: HatchService):
        self.store = store
        self.clock = clock
        self.settings = settings
        self.odds_table = TierOddsTable()
        self.hatch_service = hatch_service
        
        
    def create_room(self, member_ids: list[int], subject: str) -> RoomDTO:
        
        if not subject or not subject.strip():
            raise ValidationError(field="subject")

        if len(member_ids) < self.settings.room_min_members:
            raise ValidationError(field="member_ids")

        if len(member_ids) > self.settings.room_max_members:
            raise ValidationError(field="member_ids")

        if len(member_ids) != len(set(member_ids)):
            raise ValidationError(field="member_ids")

        for player_id in member_ids:
            running = self.store.find_running_session(player_id)

            if running is not None:
                raise InvalidStateError(f"Player {player_id} already has a running session")

        started_at = self.clock.now()

        room = GroupRoom(
            member_ids=member_ids,
            subject=subject.strip(),
            started_at=started_at,
        )

        self.store.add_group_room(room)

        for player_id in member_ids:
            self.store.create_study_session(
                player_id=player_id,
                subject=subject.strip(),
                room_id=room.id,
                started_at=started_at,
            )

        self.store.save()

        return room.to_dto()


    def get_room(self, room_id: int) -> RoomDTO:
        room = self.store.get_group_room(room_id)

        if room is None:
            raise NotFoundError("Room not found")

        return room.to_dto()


    def elapsed(self, room_id: int) -> int:
        room = self.store.get_group_room(room_id)

        if room is None:
            raise NotFoundError("Room not found")

        return self.clock.elapsed_sec(room.started_at)


    def stop(self, room_id: int) -> RoomStopResult:
        room = self.store.get_group_room(room_id)

        if room is None:
            raise NotFoundError("Room not found")

        duration = self.clock.elapsed_sec(room.started_at)
        ended_at = self.clock.now()

        room.stop(
            ended_at=ended_at,
            elapsed_sec=duration,
        )

        sessions = self.store.get_room_sessions(room_id)

        for session in sessions:
            session.stop(
                ended_at=ended_at,
                elapsed_sec=duration,
            )

        self.store.save()

        return RoomStopResult(
            room=room.to_dto(),
            duration=duration,
        )


    def hatch(self, room_id: int) -> RoomHatchResult:
        room = self.store.get_group_room(room_id)

        if room is None:
            raise NotFoundError("Room not found")

        if room.status != RoomStatus.READY:
            raise InvalidStateError("Room is not ready")

        duration = self.clock.elapsed_sec(room.started_at)

        tier = self.hatch_service.roll_tier(duration)

        sessions = self.store.get_room_sessions(room_id)

        results = []

        for session in sessions:
            result = self.hatch_service.hatch(
                session.id,
                tier,
            )
            results.append(result)

        room.mark_hatched()

        self.store.save()

        return RoomHatchResult(
            room=room.to_dto(),
            results=results,
        )