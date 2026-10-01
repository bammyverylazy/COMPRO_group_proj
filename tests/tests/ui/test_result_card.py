from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import flet as ft
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.domain.enums import EggTier, Rarity, SessionStatus
from app.dto import PetDTO, SessionReport, SpeciesDTO
from ui.result.result_card import ResultCard


@pytest.fixture
def pet() -> PetDTO:
    return PetDTO(
        species=SpeciesDTO(
            code="cat",
            name="น้องแมว",
            tier=EggTier.FRESHMAN,
            rarity=Rarity.COMMON,
            sprite_path="assets/pets/cat.png",
            description="",
        ),
        level=2,
        scale=1.5,
    )


@pytest.fixture
def base_report(pet: PetDTO) -> SessionReport:
    return SessionReport(
        session_id=1,
        player_id=1,
        subject="Mathematics",
        status=SessionStatus.HATCHED,
        is_success=True,
        duration_sec=1800,
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc),
        remaining_sec=0,
        tier=EggTier.FRESHMAN,
        pet=pet,
        is_new=False,
        room_id=None,
    )


class TestResultCard:
    def test_build_success_existing_pet(self, base_report: SessionReport) -> None:
        card = ResultCard(report=base_report, nickname="Student1")
        container = card.build()

        assert isinstance(container, ft.Container)
        assert container.bgcolor == ResultCard.CARD_COLOR

        column = container.content
        assert isinstance(column, ft.Column)
        assert len(column.controls) == 1

        success_column = column.controls[0]
        assert isinstance(success_column, ft.Column)

        badge_text = success_column.controls[4]
        assert badge_text.value == f"LEVEL UP! Lv.{base_report.pet.level}"

        image = success_column.controls[2]
        expected_size = int(ResultCard.SPRITE_SIZE * base_report.pet.scale)
        assert image.width == expected_size
        assert image.height == expected_size

    def test_build_success_new_pet(self, base_report: SessionReport) -> None:
        base_report.is_new = True
        card = ResultCard(report=base_report, nickname="Student1")
        container = card.build()

        success_column = container.content.controls[0]
        badge_text = success_column.controls[4]
        assert badge_text.value == "ตัวใหม่!"

    def test_build_failed(self, base_report: SessionReport) -> None:
        base_report.is_success = False
        base_report.duration_sec = 600
        base_report.remaining_sec = 150

        card = ResultCard(report=base_report, nickname="Student1")
        container = card.build()

        failed_column = container.content.controls[0]
        assert isinstance(failed_column, ft.Column)

        status_text = failed_column.controls[1].value
        remaining_text = failed_column.controls[3].value

        assert status_text == "ยังไม่ได้ไข่"
        assert remaining_text == "ต้องอ่านอีก 3 นาที"

    def test_build_with_room_id(self, base_report: SessionReport) -> None:
        base_report.room_id = 123
        card = ResultCard(report=base_report, nickname="AwesomeUser")
        container = card.build()

        column = container.content
        assert len(column.controls) == 2

        header_text = column.controls[0]
        assert isinstance(header_text, ft.Text)
        assert header_text.value == "AwesomeUser"
        assert header_text.size == ResultCard.TITLE_SIZE

    def test_build_without_room_id(self, base_report: SessionReport) -> None:
        base_report.room_id = None
        card = ResultCard(report=base_report, nickname="AwesomeUser")
        container = card.build()

        column = container.content
        assert len(column.controls) == 1

    @pytest.mark.parametrize(
        ("tier", "expected_name"),
        [
            (EggTier.FRESHMAN, "ไข่รุ่นเรา"),
            (EggTier.SENIOR, "ไข่รุ่นพี่"),
            (EggTier.PROFESSOR, "ไข่อาจารย์"),
        ],
    )
    def test_tier_names_mapping(self, base_report: SessionReport, tier: EggTier, expected_name: str) -> None:
        base_report.tier = tier
        card = ResultCard(report=base_report, nickname="User")
        container = card.build()

        success_column = container.content.controls[0]
        tier_text = success_column.controls[1].value

        assert tier_text == expected_name