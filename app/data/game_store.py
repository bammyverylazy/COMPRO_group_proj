from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from app.data.repositories import (
    PetRepository,
    PlayerRepository,
    RoomRepository,
    SessionRepository,
    SpeciesRepository,
)
from app.data.save_file import MemorySaveFile, SaveFile
from app.data.species_loader import SpeciesLoader

if TYPE_CHECKING:
    from app.config import Settings
    from app.data.base_repository import BaseRepository


class GameStore:
    def __init__(self, save_file: SaveFile | MemorySaveFile) -> None:
        self.save_file = save_file
        self.players: PlayerRepository = PlayerRepository()
        self.species: SpeciesRepository = SpeciesRepository()
        self.sessions: SessionRepository = SessionRepository()
        self.pets: PetRepository = PetRepository()
        self.rooms: RoomRepository = RoomRepository()

    @classmethod
    def open(cls, settings: Settings, save_file: SaveFile | MemorySaveFile | None = None) -> GameStore:
        store = cls(save_file if save_file is not None else SaveFile(Path(settings.save_path)))
        for species in SpeciesLoader(Path(settings.species_seed_path)).load():
            store.species.add(species)
        store.load()
        return store

    def load(self) -> None:
        data = self.save_file.read()
        for name, repository in self._saved_repositories().items():
            repository.load(data.get(name, []))

    def save(self) -> None:
        data = {name: repository.dump()
                for name, repository in self._saved_repositories().items()}
        self.save_file.write(data)

    def _saved_repositories(self) -> dict[str, BaseRepository[Any]]:
        return {
            "players": self.players,
            "sessions": self.sessions,
            "pets": self.pets,
            "rooms": self.rooms,
        }
