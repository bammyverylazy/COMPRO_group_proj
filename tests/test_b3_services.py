from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.config import Settings
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.domain.enums import EggTier, RoomStatus, SessionStatus
from app.domain.stats_calculator import StatsCalculator
from app.errors import InvalidStateError, ValidationError
from app.services.analytics_service import AnalyticsService
from app.services.dex_service import DexService
from app.services.focus_service import FocusSessionService
from app.services.hatch_service import HatchService
from app.services.player_service import PlayerService
from app.services.room_service import RoomService
from app.services.sanctuary_service import SanctuaryService

SPECIES = [
    {"code": f"{tier[0]}_{rarity}", "name": f"{tier} {rarity}", "tier": tier, "rarity": rarity, "sprite_path": f"sprites/{tier[0]}_{rarity}.png"}
    for tier in ("freshman", "senior", "professor")
    for rarity in ("common", "rare", "epic", "legendary")
]


class FakeClock(Clock):
    def __init__(self) -> None:
        super().__init__(1.0)
        self.current = datetime(2026, 9, 30, 9, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self.current

    def advance(self, minutes: int) -> None:
        self.current += timedelta(minutes=minutes)


@pytest.fixture
def app(tmp_path: Path):
    seed = tmp_path / "species.json"
    seed.write_text(json.dumps(SPECIES), encoding="utf-8")
    settings = Settings(save_path=str(tmp_path / "save.json"), species_seed_path=str(seed))
    store = GameStore.open(settings)
    clock = FakeClock()
    hatch = HatchService(store)
    players = PlayerService(store, clock)
    ids = [players.create_player(name).id for name in ("JJ", "Bam", "Aim", "Pin", "Pai", "Muay", "Karn")]
    return {
        "store": store,
        "clock": clock,
        "settings": settings,
        "ids": ids,
        "focus": FocusSessionService(store, clock, settings),
        "rooms": RoomService(store, clock, settings, hatch),
        "sanctuary": SanctuaryService(store),
        "dex": DexService(store),
        "analytics": AnalyticsService(store, settings),
        "hatch": hatch,
    }


def test_start_empty_subject(app):
    with pytest.raises(ValidationError):
        app["focus"].start(app["ids"][0], "   ")


def test_start_while_running(app):
    app["focus"].start(app["ids"][0], "calculus")
    with pytest.raises(InvalidStateError):
        app["focus"].start(app["ids"][0], "physics")


def test_stop_before_15_minutes_fails(app):
    session = app["focus"].start(app["ids"][0], "calculus")
    app["clock"].advance(10)
    result = app["focus"].stop(session.id)
    assert result.status is SessionStatus.FAILED
    assert result.tier_odds == {}


def test_stop_after_30_minutes_ready(app):
    session = app["focus"].start(app["ids"][0], "calculus")
    app["clock"].advance(30)
    result = app["focus"].stop(session.id)
    assert result.status is SessionStatus.READY_TO_HATCH
    assert result.tier_odds == {EggTier.FRESHMAN: 55, EggTier.SENIOR: 35, EggTier.PROFESSOR: 10}


def test_recent_subjects_unique_latest_first(app):
    for subject in ("calculus", "physics", "calculus"):
        session = app["focus"].start(app["ids"][0], subject)
        app["clock"].advance(1)
        app["focus"].stop(session.id)
    assert app["focus"].recent_subjects(app["ids"][0]) == ["calculus", "physics"]


@pytest.mark.parametrize("count", [1, 7])
def test_create_room_member_count(app, count):
    with pytest.raises(ValidationError):
        app["rooms"].create_room(app["ids"][:count], "OOP")


def test_create_room_member_running(app):
    app["focus"].start(app["ids"][1], "physics")
    with pytest.raises(InvalidStateError):
        app["rooms"].create_room(app["ids"][:3], "OOP")


def test_room_stop_before_15_all_fail(app):
    room = app["rooms"].create_room(app["ids"][:3], "OOP")
    app["clock"].advance(10)
    result = app["rooms"].stop(room.id)
    assert result.status is RoomStatus.FAILED
    statuses = {app["store"].sessions.get(sid).status for sid in room.session_ids}
    assert statuses == {SessionStatus.FAILED}
    with pytest.raises(InvalidStateError):
        app["rooms"].hatch(room.id)


def test_room_hatch_same_tier_for_all(app):
    room = app["rooms"].create_room(app["ids"][:4], "OOP")
    app["clock"].advance(95)
    app["rooms"].stop(room.id)
    result = app["rooms"].hatch(room.id)
    assert len(result.results) == 4
    assert {r.tier for r in result.results} == {result.tier}
    assert app["rooms"].get_room(room.id).status is RoomStatus.HATCHED
    reports = app["analytics"].room_reports(room.id)
    assert all(r.is_success and r.tier is result.tier for r in reports)


def test_list_pets_empty(app):
    assert app["sanctuary"].list_pets(app["ids"][0]) == []


def test_dex_all_species_and_completion(app):
    pid = app["ids"][0]
    entries = app["dex"].list_entries(pid)
    assert len(entries) == len(SPECIES)
    assert [e.species.tier for e in entries] == sorted([e.species.tier for e in entries], key=list(EggTier).index)
    for _ in range(3):
        session = app["focus"].start(pid, "calculus")
        app["clock"].advance(60)
        app["focus"].stop(session.id)
        app["hatch"].hatch(session.id)
    owned = len(app["store"].pets.list_by_player(pid))
    assert app["dex"].completion(pid) == owned / len(SPECIES)
    pet = app["store"].pets.list_by_player(pid)[0]
    entry = app["dex"].get_entry(pid, pet.species_code)
    assert entry.unlocked and entry.subjects == ["calculus"]


def test_report_failed_remaining(app):
    session = app["focus"].start(app["ids"][0], "calculus")
    app["clock"].advance(10)
    app["focus"].stop(session.id)
    report = app["analytics"].session_report(session.id)
    assert report.remaining_sec == 5 * 60
    assert report.is_success is False


def test_report_running_raises(app):
    session = app["focus"].start(app["ids"][0], "calculus")
    with pytest.raises(InvalidStateError):
        app["analytics"].session_report(session.id)


def test_history_stats(app):
    pid = app["ids"][0]
    for minutes, subject in ((10, "physics"), (40, "calculus")):
        session = app["focus"].start(pid, subject)
        app["clock"].advance(minutes)
        app["focus"].stop(session.id)
        if minutes >= 15:
            app["hatch"].hatch(session.id)
    history = app["analytics"].history(pid)
    stats = history.stats
    assert stats.total_sessions == 2
    assert (stats.success_count, stats.fail_count) == (1, 1)
    assert stats.success_rate == 0.5
    assert list(stats.subject_study_sec) == ["calculus", "physics"]
    assert sum(stats.tier_counts.values()) == 1


def test_stats_empty():
    stats = StatsCalculator().compute([], date(2026, 9, 30))
    assert stats.success_rate == 0.0
    assert set(stats.tier_counts) == set(EggTier)
    assert len(stats.daily_study_sec) == 7
