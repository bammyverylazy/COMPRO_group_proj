import math
from unittest.mock import MagicMock

import flet as ft
import pytest

from app.domain.enums import EggTier
from app.dto import SessionReport
from ui.cards.result_card import ResultCard  # ปรับ path ตามโครงสร้างโปรเจกต์ของคุณ


@pytest.fixture
def mock_pet():
    pet = MagicMock()
    pet.scale = 1.5
    pet.level = 2
    pet.species.sprite_path = "assets/pets/cat.png"
    pet.species.name = "น้องแมว"
    return pet


@pytest.fixture
def base_report(mock_pet):
    return SessionReport(
        is_success=True,
        is_new=False,
        subject="Mathematics",
        tier=EggTier.FRESHMAN,
        duration_sec=1800,
        remaining_sec=0,
        room_id=None,
        pet=mock_pet,
    )


class TestResultCard:
    # -------------------------------------------------------------------------
    # 1. Test Case: Success States
    # -------------------------------------------------------------------------

    def test_build_success_existing_pet(self, base_report):
        """กรณีอ่านสำเร็จและเลเวลอัพ (สัตว์เลี้ยงตัวเดิม)"""
        card = ResultCard(report=base_report, nickname="Student1")
        container = card.build()

        assert isinstance(container, ft.Container)
        assert container.bgcolor == ResultCard.CARD_COLOR

        column = container.content
        assert isinstance(column, ft.Column)
        assert len(column.controls) == 1  # ไม่มี room_id -> มีแค่ body

        success_column = column.controls[0]
        assert isinstance(success_column, ft.Column)

        # ตรวจสอบ Badge แสดงข้อความ LEVEL UP
        badge_text = success_column.controls[4]
        assert badge_text.value == f"LEVEL UP! Lv.{base_report.pet.level}"

        # ตรวจสอบขนาดของ Sprite Image (SPRITE_SIZE * scale)
        image = success_column.controls[2]
        expected_size = int(ResultCard.SPRITE_SIZE * base_report.pet.scale)
        assert image.width == expected_size
        assert image.height == expected_size

    def test_build_success_new_pet(self, base_report):
        """กรณีอ่านสำเร็จและได้สัตว์เลี้ยงตัวใหม่ (is_new = True)"""
        base_report.is_new = True
        card = ResultCard(report=base_report, nickname="Student1")
        container = card.build()

        success_column = container.content.controls[0]
        badge_text = success_column.controls[4]

        assert badge_text.value == "ตัวใหม่!"

    # -------------------------------------------------------------------------
    # 2. Test Case: Failure State
    # -------------------------------------------------------------------------

    def test_build_failed(self, base_report):
        """กรณีอ่านไม่สำเร็จ (ยังไม่ได้ไข่)"""
        base_report.is_success = False
        base_report.duration_sec = 600
        base_report.remaining_sec = 150  # 150 วิ = 2.5 นาที -> ceil ควรได้ 3 นาที

        card = ResultCard(report=base_report, nickname="Student1")
        container = card.build()

        failed_column = container.content.controls[0]
        assert isinstance(failed_column, ft.Column)

        # ตรวจสอบข้อความเตือนการอ่านไม่ครบ
        status_text = failed_column.controls[1].value
        remaining_text = failed_column.controls[3].value

        assert status_text == "ยังไม่ได้ไข่"
        assert remaining_text == "ต้องอ่านอีก 3 นาที"

    # -------------------------------------------------------------------------
    # 3. Test Case: Room ID & Header Controls
    # -------------------------------------------------------------------------

    def test_build_with_room_id(self, base_report):
        """กรณีมี room_id ต้องมี Text แสดง Nickname ที่ตำแหน่งแรก"""
        base_report.room_id = "ROOM_123"
        card = ResultCard(report=base_report, nickname="AwesomeUser")
        container = card.build()

        column = container.content
        assert len(column.controls) == 2  # มี Header (Nickname) + Body

        header_text = column.controls[0]
        assert isinstance(header_text, ft.Text)
        assert header_text.value == "AwesomeUser"
        assert header_text.size == ResultCard.TITLE_SIZE

    def test_build_without_room_id(self, base_report):
        """กรณีไม่มี room_id จะต้องไม่มี Text แสดง Nickname"""
        base_report.room_id = None
        card = ResultCard(report=base_report, nickname="AwesomeUser")
        container = card.build()

        column = container.content
        assert len(column.controls) == 1

    # -------------------------------------------------------------------------
    # 4. Test Case: Tier Names Mapping
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("tier", "expected_name"),
        [
            (EggTier.FRESHMAN, "ไข่รุ่นเรา"),
            (EggTier.SENIOR, "ไข่รุ่นพี่"),
            (EggTier.PROFESSOR, "ไข่อาจารย์"),
        ],
    )
    def test_tier_names_mapping(self, base_report, tier, expected_name):
        """ทดสอบการแปลง Enum EggTier เป็นชื่อภาษาไทย"""
        base_report.tier = tier
        card = ResultCard(report=base_report, nickname="User")
        container = card.build()

        success_column = container.content.controls[0]
        tier_text = success_column.controls[1].value

        assert tier_text == expected_name