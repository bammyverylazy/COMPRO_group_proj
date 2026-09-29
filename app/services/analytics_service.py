from __future__ import annotations

from datetime import date

from app.config import Settings
from app.data.game_store import GameStore
from app.domain.enums import SessionStatus
from app.domain.pet_policy import PetLevelPolicy
from app.domain.stats_calculator import StatsCalculator
from app.domain.study_session import StudySession
from app.dto import History, PetDTO, SessionReport
from app.errors import InvalidStateError


class AnalyticsService:
    FINISHED: tuple[SessionStatus, ...] = (SessionStatus.FAILED, SessionStatus.HATCHED)

    def __init__(self, store: GameStore, settings: Settings) -> None:
        self.store = store
        self.settings = settings
        self.policy = PetLevelPolicy()
        self.calculator = StatsCalculator()

    def session_report(self, session_id: int) -> SessionReport:
        session = self.store.sessions.get(session_id)
        if session.status not in self.FINISHED:
            raise InvalidStateError("รอบนี้ยังไม่จบ")
        min_success_sec = self.settings.min_success_minutes * 60
        remaining_sec = max(0, min_success_sec - session.duration_sec) if session.status is SessionStatus.FAILED else 0
        return SessionReport(
            session_id=session.id,
            player_id=session.player_id,
            subject=session.subject,
            status=session.status,
            is_success=session.is_success(),
            duration_sec=session.duration_sec,
            started_at=session.started_at,
            ended_at=session.ended_at,
            remaining_sec=remaining_sec,
            tier=session.tier,
            pet=self._pet_for(session),
            is_new=self._is_new(session),
            room_id=session.room_id,
        )

    def room_reports(self, room_id: int) -> list[SessionReport]:
        room = self.store.rooms.get(room_id)
        return [self.session_report(session_id) for session_id in room.session_ids]

    def history(self, player_id: int) -> History:
        sessions = [
            session
            for session in self.store.sessions.list_by_player(player_id)
            if session.status in self.FINISHED
        ]
        reports = [self.session_report(session.id) for session in sessions]
        return History(reports=reports, stats=self.calculator.compute(reports, date.today()))

    def _pet_for(self, session: StudySession) -> PetDTO | None:
        if session.species_code is None:
            return None
        pet = self.store.pets.find_owned(session.player_id, session.species_code)
        species = self.store.species.find(session.species_code)
        if pet is None or species is None:
            return None
        return pet.to_dto(species, self.policy)

    def _is_new(self, session: StudySession) -> bool | None:
        if session.species_code is None:
            return None
        same_species = [
            other
            for other in self.store.sessions.list_by_player(session.player_id)
            if other.species_code == session.species_code
        ]
        first = min(same_species, key=lambda other: (other.ended_at or other.started_at, other.id))
        return first.id == session.id
