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

    def __init__(self, store: GameStore, clock: Clock, settings: Settings):
        self.store = store
        self.clock = clock
        self.settings = settings
        self.odds_table = TierOddsTable()
        

    def start(self, player_id: int, subject: str, room_id: int | None = None) -> SessionDTO:

        if not subject:
            raise ValidationError(field="subject")

        if self.get_running(player_id) is not None:
            raise InvalidStateError()

        session = StudySession(
            player_id=player_id,
            subject=subject,
            room_id=room_id,
            started_at=self.clock.now()
        )

        self.store.save(session)

        return session.to_dto()
    

    def get_running(self, player_id: int) -> SessionDTO | None:

        sessions = self.store.get_sessions(player_id)

        for session in sessions:
            if session.status == SessionStatus.RUNNING:
                return session.to_dto()

        return None


    def elapsed(self, session_id: int) -> int:

        session = self.store.get_session(session_id)
        
        return self.clock.elapsed_sec(session.started_at)


    def stop(self, session_id: int) -> StopResult:

        session = self.store.get_session(session_id)

        elapsed = self.clock.elapsed_sec(session.started_at)

        tier_odds = self.odds_table.get_odds(elapsed)

        result = session.stop(
            elapsed=elapsed,
            tier_odds=tier_odds
        )

        self.store.save(session)

        return result


    def recent_subjects(self, player_id: int, limit: int = 5) -> list[str]:

        sessions = self.store.get_sessions(player_id)
        result = []

        for session in reversed(sessions):

            if session.subject not in result:
                result.append(session.subject)

            if len(result) == limit:
                break

        return result
    