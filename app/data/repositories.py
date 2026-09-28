
from __future__ import annotations

from typing import Any

from app.data.base_repository import BaseRepository
from app.domain.enums import EggTier, Rarity, SessionStatus
from app.domain.group_room import GroupRoom
from app.domain.owned_pet import OwnedPet
from app.domain.player import Player
from app.domain.species import Species
from app.domain.study_session import StudySession


class PlayerRepository(BaseRepository[Player]):
    def key_of(self, item: Player) -> int:
        return item.id

    def item_from_dict(self, data: dict[str, Any]) -> Player:
        return Player.from_dict(data)

    def find_by_nickname(self, nickname: str) -> Player | None:
        target = nickname.strip().casefold()
        return next((player for player in self.list_all() if player.nickname.casefold() == target), None)


class SpeciesRepository(BaseRepository[Species]):
    def key_of(self, item: Species) -> str:
        return item.code

    def item_from_dict(self, data: dict[str, Any]) -> Species:
        return Species(
            code=data["code"],
            name=data["name"],
            tier=EggTier(data["tier"]),
            rarity=Rarity(data["rarity"]),
            sprite_path=data["sprite_path"],
            description=data.get("description", ""),
        )

    def list_by_tier(self, tier: EggTier) -> list[Species]:
        return [species for species in self.list_all() if species.tier is tier]


class SessionRepository(BaseRepository[StudySession]):
    def key_of(self, item: StudySession) -> int:
        return item.id

    def item_from_dict(self, data: dict[str, Any]) -> StudySession:
        return StudySession.from_dict(data)

    def get_running(self, player_id: int) -> StudySession | None:
        return next(
            (
                session
                for session in self.list_all()
                if session.player_id == player_id and session.status is SessionStatus.RUNNING
            ),
            None,
        )

    def list_by_player(self, player_id: int) -> list[StudySession]:
        sessions = [session for session in self.list_all(
        ) if session.player_id == player_id]
        return sorted(sessions, key=lambda session: session.started_at, reverse=True)


class PetRepository(BaseRepository[OwnedPet]):
    def key_of(self, item: OwnedPet) -> tuple[int, str]:
        return (item.player_id, item.species_code)

    def item_from_dict(self, data: dict[str, Any]) -> OwnedPet:
        return OwnedPet.from_dict(data)

    def find_owned(self, player_id: int, species_code: str) -> OwnedPet | None:
        return self.find((player_id, species_code))

    def list_by_player(self, player_id: int) -> list[OwnedPet]:
        pets = [pet for pet in self.list_all() if pet.player_id == player_id]
        return sorted(pets, key=lambda pet: pet.hatched_at)


class RoomRepository(BaseRepository[GroupRoom]):
    def key_of(self, item: GroupRoom) -> int:
        return item.id

    def item_from_dict(self, data: dict[str, Any]) -> GroupRoom:
        return GroupRoom.from_dict(data)
