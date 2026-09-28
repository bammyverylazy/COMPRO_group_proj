# B3 · Session, Room & Stats (Backend)

การอ่านเดี่ยว, ห้องกลุ่ม Shared Fate, ห้องภาค, Dex, Analytics (ฝั่ง service)

> อ่าน [00-shared.md](00-shared.md) ก่อน: วิธีทำงานแบบแยกฝั่ง, กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **ฝั่ง:** Backend อย่างเดียว · ไม่ต้อง import flet
- **Class ที่ต้องเขียน (6):** `FocusSessionService`, `RoomService`, `SanctuaryService`, `DexService`, `StatsCalculator`, `AnalyticsService`
- **method ในไฟล์ของคนอื่น:** `StudySession` (ไฟล์ของ B1), `GroupRoom` (ไฟล์ของ B1)
- **ใช้ของใคร:** B1 (`GameStore`, `Clock`, model ทั้งหมด) · B2 (`TierOddsTable`, `HatchService`, `PetLevelPolicy`, `OwnedPet.to_dto`)
- **ใครใช้ของเรา:** F2 ผ่าน `ctx.focus` · F3 ผ่าน `ctx.rooms`, `ctx.analytics` · F4 ผ่าน `ctx.sanctuary`, `ctx.dex`, `ctx.rooms.hatch`
- **branch:** `feat/b3-session-room-stats`

## Backend

**Import ที่ต้องใช้ (รวมทุกไฟล์ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from datetime import date
from typing import ClassVar

from app.config import Settings
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.domain.enums import EggTier, Rarity, RoomStatus, SessionStatus
from app.domain.group_room import GroupRoom
from app.domain.pet_policy import PetLevelPolicy
from app.domain.study_session import StudySession
from app.domain.tier_odds_table import TierOddsTable
from app.dto import DexEntry, History, HistoryStats, PetDTO, RoomDTO, RoomHatchResult, RoomStopResult, SessionDTO, SessionReport, StopResult
from app.errors import InvalidStateError, NotFoundError, ValidationError
from app.services.hatch_service import HatchService
```

### `FocusSessionService`

- **ไฟล์:** `app/services/focus_service.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `FocusSessionService(store, clock, settings)`
- **หน้าที่:** เริ่ม / ดูเวลา / หยุด การอ่านเดี่ยว

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง |
| `clock` | `Clock` | ต้องส่งตอนสร้าง | นาฬิกากลาง |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | ค่าตั้งค่า |
| `odds_table` | `TierOddsTable` | สร้างใน `__init__` = `TierOddsTable()` | ตารางโอกาสไข่ตามเวลา |

| method | return | ทำอะไร |
|---|---|---|
| `start(player_id: int, subject: str, room_id: int \| None = None)` | `SessionDTO` | subject ว่าง → ValidationError(field="subject") · ผู้เล่นมี RUNNING อยู่ → InvalidStateError · save() |
| `get_running(player_id: int)` | `SessionDTO \| None` | รอบที่ค้างอยู่ |
| `elapsed(session_id: int)` | `int` | clock.elapsed_sec(started_at) |
| `stop(session_id: int)` | `StopResult` | session.stop(...) · tier_odds จาก odds_table · save() |
| `recent_subjects(player_id: int, limit: int = 5)` | `list[str]` | วิชาที่อ่านล่าสุด ไม่ซ้ำ |

### `RoomService`

- **ไฟล์:** `app/services/room_service.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `RoomService(store, clock, settings, hatch_service)`
- **หน้าที่:** ห้องอ่านกลุ่มบนเครื่องเดียว ชะตาเดียวกัน: หยุดก่อน 15 นาที ทุกคนไม่ได้ไข่ · ถึงแล้วสุ่มระดับไข่ครั้งเดียว ทุกคนได้ระดับเดียวกัน แต่สุ่มสัตว์ของใครของมัน

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง |
| `clock` | `Clock` | ต้องส่งตอนสร้าง | นาฬิกากลาง |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | ค่าตั้งค่า |
| `hatch_service` | `HatchService` | ต้องส่งตอนสร้าง | B2 |
| `odds_table` | `TierOddsTable` | สร้างใน `__init__` = `TierOddsTable()` | ตารางโอกาสไข่ตามเวลา |

| method | return | ทำอะไร |
|---|---|---|
| `create_room(member_ids: list[int], subject: str)` | `RoomDTO` | เช็กจำนวนสมาชิก min/max, ไม่ซ้ำ, ไม่มีใคร RUNNING อยู่ → สร้าง StudySession ให้ทุกคน (room_id เดียวกัน, started_at เดียวกัน) + GroupRoom · save() |
| `get_room(room_id: int)` | `RoomDTO` | ไม่เจอ → NotFoundError |
| `elapsed(room_id: int)` | `int` | clock.elapsed_sec(room.started_at) |
| `stop(room_id: int)` | `RoomStopResult` | room.stop + session.stop ของทุกคนด้วยเวลาเดียวกัน · save() |
| `hatch(room_id: int)` | `RoomHatchResult` | ไม่ READY → InvalidStateError · tier = hatch_service.roll_tier(duration) ครั้งเดียว → hatch_service.hatch(session_id, tier) ทุกคน → room.mark_hatched · save() |

### `SanctuaryService`

- **ไฟล์:** `app/services/sanctuary_service.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `SanctuaryService(store)`
- **หน้าที่:** สัตว์ของผู้เล่นไปโชว์ในห้องภาค

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` | B2 |

| method | return | ทำอะไร |
|---|---|---|
| `list_pets(player_id: int)` | `list[PetDTO]` | ทุกตัว + level + scale |
| `count_pets(player_id: int)` | `int` | จำนวนชนิดที่มี |

### `DexService`

- **ไฟล์:** `app/services/dex_service.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `DexService(store)`
- **หน้าที่:** ข้อมูล CPE Dex: ทุกชนิด พร้อมบอกว่าปลดล็อกหรือยัง

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง |

| method | return | ทำอะไร |
|---|---|---|
| `list_entries(player_id: int)` | `list[DexEntry]` | ทุกชนิด เรียง tier แล้ว rarity |
| `get_entry(player_id: int, species_code: str)` | `DexEntry` | หนึ่งชนิด + subjects จาก session ที่ได้ตัวนี้ |
| `completion(player_id: int)` | `float` | ชนิดที่ปลดล็อก / ทั้งหมด |

### `StatsCalculator`

- **ไฟล์:** `app/domain/stats_calculator.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `StatsCalculator()`
- **หน้าที่:** คำนวณสถิติจาก list ของ SessionReport (Python ล้วน เทสต์ง่าย)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `DAYS_IN_CHART` | `int` | ค่าคงที่ของ class `= 7` | กราฟรายวันกี่วัน |

| method | return | ทำอะไร |
|---|---|---|
| `compute(reports: list[SessionReport], today: date)` | `HistoryStats` | รวมทุกค่าใน HistoryStats |
| `success_rate(reports: list[SessionReport])` | `float` | 0 รอบ → 0.0 |
| `tier_counts(reports: list[SessionReport])` | `dict[EggTier, int]` | ทุก tier มี key แม้ค่า 0 |
| `subject_study_sec(reports: list[SessionReport])` | `dict[str, int]` | เรียงมากไปน้อย |
| `daily_study_sec(reports: list[SessionReport], today: date)` | `dict[str, int]` | DAYS_IN_CHART วันล่าสุด วันที่ไม่ได้อ่าน = 0 |

### `AnalyticsService`

- **ไฟล์:** `app/services/analytics_service.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `AnalyticsService(store, settings)`
- **หน้าที่:** สรุปผลรายรอบ รายห้อง และประวัติ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | ค่าตั้งค่า |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` | B2 |
| `calculator` | `StatsCalculator` | สร้างใน `__init__` = `StatsCalculator()` | ตัวคำนวณสถิติ |

| method | return | ทำอะไร |
|---|---|---|
| `session_report(session_id: int)` | `SessionReport` | RUNNING หรือ READY_TO_HATCH → InvalidStateError · remaining_sec = max(0, min_success − duration) |
| `room_reports(room_id: int)` | `list[SessionReport]` | report ของสมาชิกทุกคน |
| `history(player_id: int)` | `History` | ทุกรอบที่จบแล้วของผู้เล่น + stats |

## Method ที่ต้องเขียนในไฟล์ของคนอื่น

ตัวแปรของ class เหล่านี้ B1 สร้างไว้แล้ว ให้เพิ่มเฉพาะ method ข้างล่าง

### `StudySession`

- **ไฟล์:** `app/domain/study_session.py` (ของ B1)

| method | return | ทำอะไร |
|---|---|---|
| `stop(ended_at: datetime, duration_sec: int, min_success_sec: int)` | `SessionStatus` | บันทึกเวลา แล้วเปลี่ยนเป็น FAILED หรือ READY_TO_HATCH · ไม่ได้ RUNNING → InvalidStateError |
| `can_hatch()` | `bool` | True ถ้า READY_TO_HATCH |
| `mark_hatched(tier: EggTier, species_code: str)` | `None` | บันทึกไข่ + สัตว์ แล้วเปลี่ยนเป็น HATCHED · ไม่ได้ READY_TO_HATCH → InvalidStateError |
| `is_running()` | `bool` | True ถ้า RUNNING |
| `is_success()` | `bool` | True ถ้า HATCHED |
| `to_dto()` | `SessionDTO` | แปลงเป็น SessionDTO |

### `GroupRoom`

- **ไฟล์:** `app/domain/group_room.py` (ของ B1)

| method | return | ทำอะไร |
|---|---|---|
| `stop(ended_at: datetime, duration_sec: int, min_success_sec: int)` | `RoomStatus` | บันทึกเวลา แล้วเปลี่ยนเป็น FAILED หรือ READY_TO_HATCH |
| `can_hatch()` | `bool` | True ถ้า READY_TO_HATCH |
| `mark_hatched(tier: EggTier)` | `None` | บันทึกระดับไข่ เปลี่ยนเป็น HATCHED |
| `to_dto(members: list[PlayerDTO])` | `RoomDTO` | แปลงเป็น RoomDTO |

## เช็กลิสต์ก่อนส่ง PR

- [ ] start ชื่อวิชาว่าง → ValidationError
- [ ] start ตอนมี RUNNING อยู่ → InvalidStateError
- [ ] stop ก่อน 15 นาที → FAILED, tier_odds ว่าง
- [ ] stop หลัง 30 นาที → READY_TO_HATCH, tier_odds = 55/35/10
- [ ] create_room สมาชิก 1 คน หรือ 7 คน → ValidationError
- [ ] create_room ที่มีสมาชิก RUNNING อยู่ → InvalidStateError
- [ ] stop ก่อน 15 นาที → ทุก session FAILED
- [ ] hatch → ทุกคนได้ tier เดียวกัน และได้ HatchResult ครบทุกคน
- [ ] list_pets ผู้เล่นที่ยังไม่มีสัตว์ → []
- [ ] list_entries ครบทุกชนิดใน species.json
- [ ] completion ถูกต้องเมื่อมี 3 จาก 12 → 0.25
- [ ] session_report ของรอบ FAILED ได้ remaining_sec ถูก
- [ ] session_report ของรอบ RUNNING → InvalidStateError
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
