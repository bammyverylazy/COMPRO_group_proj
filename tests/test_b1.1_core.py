from datetime import datetime, timezone

import pytest

from app.config import Settings
from app.core.clock import Clock
from app.data.base_repository import BaseRepository
from app.domain.enums import EggTier, Rarity, RoomStatus, SessionStatus
from app.domain.group_room import GroupRoom
from app.domain.owned_pet import OwnedPet
from app.domain.player import Player
from app.domain.species import Species
from app.domain.study_session import StudySession
from app.domain.pet_policy import PetLevelPolicy
from app.dto import RoomDTO, SessionDTO
from app.errors import AppError, InvalidStateError, NotFoundError, ValidationError


class DummyRepo(BaseRepository[Player]):
    def key_of(self, item: Player):
        return item.id

    def item_from_dict(self, data: dict):
        return Player.from_dict(data)


def test_settings_defaults():
    s = Settings()
    assert s.min_success_minutes == 15
    assert s.demo_speed == 1.0
    assert s.save_path == "save.json"
    assert s.species_seed_path == "seed/species.json"
    assert s.min_room_members == 2
    assert s.max_room_members == 6


def test_clock_uses_speed_and_utc():
    clock = Clock(speed=2.0)
    started = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)
    until = datetime(2026, 9, 28, 12, 1, 30, tzinfo=timezone.utc)
    assert clock.elapsed_sec(started, until) == 180
    assert clock.now().tzinfo is not None


def test_enums_values():
    assert EggTier.FRESHMAN.value == "freshman"
    assert Rarity.LEGENDARY.value == "legendary"
    assert SessionStatus.READY_TO_HATCH.value == "ready_to_hatch"
    assert RoomStatus.HATCHED.value == "hatched"


def test_errors_raise_and_catch():
    with pytest.raises(ValidationError):
        raise ValidationError("bad input", field="subject")

    err = AppError("message", field="name")
    assert err.message == "message"
    assert err.field == "name"

    with pytest.raises(InvalidStateError):
        raise InvalidStateError("bad state")


def test_player_and_species_round_trip():
    player = Player(1, "Alice", created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert player.to_dict()["created_at"].endswith("+00:00")
    assert Player.from_dict(player.to_dict()).nickname == "Alice"

    species = Species(
        code="cat",
        name="CPE Cat",
        tier=EggTier.FRESHMAN,
        rarity=Rarity.RARE,
        sprite_path="/img/cat.png",
    )
    data = species.to_dict()
    assert data["tier"] == "freshman"
    assert Species.from_dict(data).code == "cat"


def test_study_session_and_owned_pet_round_trip():
    session = StudySession(id=7, player_id=2, subject="Math")
    data = session.to_dict()
    restored = StudySession.from_dict(data)
    assert restored.id == 7
    assert restored.status is SessionStatus.RUNNING

    pet = OwnedPet(player_id=2, species_code="cat", hatched_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    pet_data = pet.to_dict()
    restored_pet = OwnedPet.from_dict(pet_data)
    assert restored_pet.species_code == "cat"
    assert restored_pet.level == 1


def test_group_room_to_dto_is_json_safe():
    room = GroupRoom(
        id=5,
        subject="Algorithms",
        member_ids=[1, 2],
        session_ids=[10, 11],
        started_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
    )
    dto = room.to_dto(members=[])
    assert isinstance(dto.started_at, str)
    assert dto.started_at.endswith("+00:00")


def test_base_repository_behaves_like_b1_spec():
    repo = DummyRepo()
    p1 = Player(1, "A", created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    p2 = Player(2, "B", created_at=datetime(2026, 1, 2, tzinfo=timezone.utc))

    assert repo.next_id() == 1
    assert repo.add(p1) is p1
    assert repo.add(p2) is p2
    assert repo.get(1).nickname == "A"
    assert repo.find(99) is None
    assert len(repo.list_all()) == 2
    assert repo.next_id() == 3

    dumped = repo.dump()
    assert dumped[0]["id"] == 1

    repo2 = DummyRepo()
    repo2.load(dumped)
    assert repo2.get(2).nickname == "B"

    with pytest.raises(NotFoundError):
        repo.get(999)


def test_pet_policy_values():
    policy = PetLevelPolicy()
    assert policy.SCALE_STEP == 0.15
    assert policy.MAX_SCALE == 2.0
    assert policy.MAX_LEVEL == 99
    assert policy.next_level(1) == 2
    assert policy.scale_for(1) == 1.0
