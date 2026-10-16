from __future__ import annotations

from app.config import Settings
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.domain.enums import SessionStatus
from app.domain.study_session import StudySession
from app.domain.tier_odds_table import TierOddsTable
from app.dto import SessionDTO, StopResult
from app.errors import InvalidStateError, ValidationError


class FocusSessionService:
    def __init__(self, store: GameStore, clock: Clock, settings: Settings) -> None:
        self.store = store
        self.clock = clock
        self.settings = settings
        self.odds_table = TierOddsTable()

    def start(self, player_id: int, subject: str, room_id: int | None = None) -> SessionDTO:
        clean_subject = subject.strip()
        if not clean_subject:
            raise ValidationError("Please enter a subject", field="subject")
        self.store.players.get(player_id)
        if self.store.sessions.get_running(player_id) is not None:
            raise InvalidStateError("This player already has a session in progress")
        session = StudySession(
            id=self.store.sessions.next_id(),
            player_id=player_id,
            subject=clean_subject,
            started_at=self.clock.now(),
            room_id=room_id,
        )
        self.store.sessions.add(session)
        self.store.save()
        return session.to_dto()

    def get_running(self, player_id: int) -> SessionDTO | None:
        session = self.store.sessions.get_running(player_id)
        return session.to_dto() if session is not None else None

    def elapsed(self, session_id: int) -> int:
        session = self.store.sessions.get(session_id)
        if session.ended_at is not None:
            return session.duration_sec
        return self.clock.elapsed_sec(session.started_at)

    def stop(self, session_id: int) -> StopResult:
        session = self.store.sessions.get(session_id)
        if not session.is_running():
            raise InvalidStateError("This session has already stopped")
        duration_sec = self.clock.elapsed_sec(session.started_at)
        status = session.stop(self.clock.now(), duration_sec, self._min_success_sec())
        self.store.save()
        tier_odds = self.odds_table.odds_for(duration_sec) if status is SessionStatus.READY_TO_HATCH else {}
        return StopResult(
            session_id=session.id,
            status=status,
            duration_sec=duration_sec,
            tier_odds=dict(tier_odds),
        )

    def recent_subjects(self, player_id: int, limit: int = 5) -> list[str]:
        subjects: list[str] = []
        for session in self.store.sessions.list_by_player(player_id):
            if session.subject not in subjects:
                subjects.append(session.subject)
            if len(subjects) == limit:
                break
        return subjects

    def _min_success_sec(self) -> int:
        return self.settings.min_success_minutes * 60
