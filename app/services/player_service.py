from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from app.domain.player import Player
from app.errors import ValidationError

if TYPE_CHECKING:
    from app.core.clock import Clock
    from app.data.game_store import GameStore
    from app.dto import PlayerDTO


class PlayerService:
    MAX_NICKNAME_LENGTH: ClassVar[int] = 20

    def __init__(self, store: GameStore, clock: Clock) -> None:
        self.store = store
        self.clock = clock

    def list_players(self) -> list[PlayerDTO]:
        players = sorted(self.store.players.list_all(),
                         key=lambda player: player.nickname.casefold())
        return [player.to_dto() for player in players]

    def create_player(self, nickname: str) -> PlayerDTO:
        clean_nickname = nickname.strip()
        self._validate_nickname(clean_nickname)
        player = Player(
            id=self.store.players.next_id(),
            nickname=clean_nickname,
            created_at=self.clock.now(),
        )
        self.store.players.add(player)
        self.store.save()
        return player.to_dto()

    def get_player(self, player_id: int) -> PlayerDTO:
        return self.store.players.get(player_id).to_dto()

    def _validate_nickname(self, nickname: str) -> None:
        if not nickname:
            raise ValidationError("Please enter a nickname", field="nickname")
        if len(nickname) > self.MAX_NICKNAME_LENGTH:
            raise ValidationError(
                f"Nickname must be at most {self.MAX_NICKNAME_LENGTH} characters", field="nickname")
        if self.store.players.find_by_nickname(nickname) is not None:
            raise ValidationError(
                f"Nickname {nickname} is already taken", field="nickname")
