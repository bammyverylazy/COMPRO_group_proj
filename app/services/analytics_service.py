from __future__ import annotations
from datetime import date
from app.config import Settings
from app.data.game_store import GameStore
from app.domain.pet_policy import PetLevelPolicy
from app.domain.stats_calculator import StatsCalculator
from app.domain.enums import SessionStatus
from app.dto import History, HistoryStats, SessionReport
from app.errors import InvalidStateError


class AnalyticsService:
    def __init__(self, store: GameStore, settings: Settings):
        self.store = store
        self.settings = settings
        self.policy = PetLevelPolicy()
        self.calculator = StatsCalculator()
    def session_report(self, session_id: int) -> SessionReport:
        session = self.store.get_session(session_id)
        if session.status in (SessionStatus.RUNNING, SessionStatus.READY_TO_HATCH):
            raise InvalidStateError("Session is still running or waiting to hatch")

        min_success = self.settings.MIN_SUCCESS_SEC
        duration = session.duration_sec
        remaining_sec = max(0, min_success - duration)

        exp_gained = 0
        current_level = 1
        current_scale = 1.0

        if session.hatched_species_code:
            pet = self.store.get_owned_pet_by_species(session.player_id, session.hatched_species_code)
            if pet:
                exp_gained = self.settings.EXP_PER_HATCH
                current_level = self.policy.calculate_level(pet.total_exp)
                current_scale = self.policy.calculate_scale(current_level)

        return SessionReport(
            session_id=session.id,
            player_id=session.player_id,
            subject=session.subject,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_sec=duration,
            status=session.status,
            min_success_sec=min_success,
            remaining_sec=remaining_sec,
            tier=session.hatched_tier,
            species_code=session.hatched_species_code,
            exp_gained=exp_gained,
            current_level=current_level,
            current_scale=current_scale
        )

    def room_reports(self, room_id: int) -> list[SessionReport]:
        sessions = self.store.get_sessions_by_room_id(room_id)
        return [self.session_report(session.id) for session in sessions]
    def history(self, player_id: int) -> History:
        all_sessions = self.store.get_sessions_by_player_id(player_id)
        finished_sessions = [
            s for s in all_sessions 
            if s.status in (SessionStatus.FAILED, SessionStatus.HATCHED)
        ]
        
        reports = [self.session_report(session.id) for session in finished_sessions]
        stats = self.calculator.compute(reports, date.today())

        return History(
            reports=reports,
            stats=stats
        )