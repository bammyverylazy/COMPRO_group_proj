# P5 · Shared Fate

ห้องอ่านกลุ่มบนเครื่องเดียว ชะตาเดียวกัน

> อ่าน [00-shared.md](00-shared.md) ก่อน: กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **Backend (1 class):** `RoomService`
- **Frontend (4 class):** `MemberPicker`, `RoomSetupView`, `MemberList`, `RoomFocusView`
- **method ในไฟล์ของคนอื่น:** `GroupRoom`
- **ใช้ของใคร:** P1 (`GameStore`, `GroupRoom`, `PlayerService`), P2 (ของกลางหน้าจอ), P3 (`HatchService`, `TierOddsTable`, `EggOddsPanel`), P4 (`StudySession`, `StopwatchTimer`, `CpegoBot`, `CpegoBubble`)
- **ใครใช้ของเรา:** LobbyView (P6) เปิดหน้าห้องกลุ่ม · ResultView (P7) โชว์ผลของทั้งห้อง
- **branch:** `feat/shared-fate`

## Backend

**Import ที่ต้องใช้ (รวมทุกไฟล์ backend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from app.config import Settings
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.domain.enums import RoomStatus
from app.domain.group_room import GroupRoom
from app.domain.study_session import StudySession
from app.domain.tier_odds_table import TierOddsTable
from app.dto import RoomDTO, RoomHatchResult, RoomStopResult
from app.errors import InvalidStateError, NotFoundError, ValidationError
from app.services.hatch_service import HatchService
```

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
| `hatch_service` | `HatchService` | ต้องส่งตอนสร้าง | P3 |
| `odds_table` | `TierOddsTable` | สร้างใน `__init__` = `TierOddsTable()` | ตารางโอกาสไข่ตามเวลา |

| method | return | ทำอะไร |
|---|---|---|
| `create_room(member_ids: list[int], subject: str)` | `RoomDTO` | เช็กจำนวนสมาชิก min/max, ไม่ซ้ำ, ไม่มีใคร RUNNING อยู่ → สร้าง StudySession ให้ทุกคน (room_id เดียวกัน, started_at เดียวกัน) + GroupRoom · save() |
| `get_room(room_id: int)` | `RoomDTO` | ไม่เจอ → NotFoundError |
| `elapsed(room_id: int)` | `int` | clock.elapsed_sec(room.started_at) |
| `stop(room_id: int)` | `RoomStopResult` | room.stop + session.stop ของทุกคนด้วยเวลาเดียวกัน · save() |
| `hatch(room_id: int)` | `RoomHatchResult` | ไม่ READY → InvalidStateError · tier = hatch_service.roll_tier(duration) ครั้งเดียว → hatch_service.hatch(session_id, tier) ทุกคน → room.mark_hatched · save() |

## Frontend

**Import ที่ต้องใช้ (รวมทุกไฟล์ frontend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from typing import Any, Callable, ClassVar, TYPE_CHECKING

import flet as ft

from app.domain.enums import EggTier, RoomStatus
from app.dto import PlayerDTO, RoomDTO
from app.errors import AppError, ValidationError
from ui.core.base_view import BaseView
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.widgets import ConfirmDialog, PixelButton
from ui.focus.cpego_bot import CpegoBot
from ui.focus.cpego_bubble import CpegoBubble
from ui.focus.stopwatch_timer import StopwatchTimer
from ui.hatch.egg_odds_panel import EggOddsPanel

if TYPE_CHECKING:
    from ui.core.app_context import AppContext
```

### `MemberPicker`

- **ไฟล์:** `ui/room/member_picker.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `MemberPicker(players, on_create, max_members)`
- **หน้าที่:** เลือกสมาชิกห้อง: checkbox รายชื่อผู้เล่น + ช่องเพิ่มชื่อเล่นใหม่

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `players` | `list[PlayerDTO]` | ต้องส่งตอนสร้าง | ผู้เล่นทั้งหมด |
| `on_create` | `Callable[[str], PlayerDTO]` | ต้องส่งตอนสร้าง | สร้างผู้เล่นใหม่แล้วคืน PlayerDTO |
| `max_members` | `int` | ต้องส่งตอนสร้าง | จาก Settings |
| `selected_ids` | `set[int]` | สร้างใน `__init__` = `set()` | player_id ที่ติ๊ก |
| `nickname_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` | ช่องชื่อเล่น |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `toggle(player_id: int)` | `None` | ติ๊ก/เอาออก เกิน max ไม่ให้ติ๊ก |
| `add_player()` | `None` | on_create(ชื่อ) แล้วติ๊กให้อัตโนมัติ |
| `selected` *@property* | `list[int]` | ทำตาม class แม่ |

### `RoomSetupView`

- **ไฟล์:** `ui/room/room_setup_view.py`
- **ชนิด:** class
- **inherit:** `BaseView`
- **สร้าง:** `RoomSetupView(ctx, **params)`
- **หน้าที่:** หน้าตั้งห้องกลุ่ม: เลือกสมาชิก, ชื่อวิชา, START / BACK (ผู้เล่นปัจจุบันถูกติ๊กไว้ก่อน)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/room/setup"` | path ของหน้า |
| `picker` | `MemberPicker \| None` | สร้างใน `__init__` = `None` | ตัวเลือกผู้เล่น |
| `subject_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` | ช่องชื่อวิชา |
| `error_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความเตือนสีแดง |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `start()` | `None` | ctx.rooms.create_room → ไป /room (room_id) · ValidationError → error_text |
| `back()` | `None` | ไป /lobby |

### `MemberList`

- **ไฟล์:** `ui/room/member_list.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `MemberList(members)`
- **หน้าที่:** แถวสมาชิกในห้อง (ชื่อ + รูปไข่เล็ก)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `members` | `list[PlayerDTO]` | ต้องส่งตอนสร้าง | สมาชิก |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `set_egg_odds(odds: dict[EggTier, int])` | `None` | ไข่ของทุกคนเปลี่ยนพร้อมกัน |

### `RoomFocusView`

- **ไฟล์:** `ui/room/room_focus_view.py`
- **ชนิด:** class
- **inherit:** `BaseView`
- **สร้าง:** `RoomFocusView(ctx, **params)`
- **หน้าที่:** หน้าอ่านกลุ่ม: นาฬิกาเดียว, รายชื่อสมาชิก, ไข่, CPEGO, STOP (ข้อความยืนยันบอกว่าทุกคนจะได้ผลเดียวกัน)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/room"` | path ของหน้า |
| `room` | `RoomDTO \| None` | สร้างใน `__init__` = `None` | params["room_id"] |
| `timer` | `StopwatchTimer \| None` | สร้างใน `__init__` = `None` | P4 |
| `time_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความเวลา 67:07 |
| `members` | `MemberList \| None` | สร้างใน `__init__` = `None` | สมาชิก |
| `odds_panel` | `EggOddsPanel \| None` | สร้างใน `__init__` = `None` | P3 |
| `bot` | `CpegoBot \| None` | สร้างใน `__init__` = `None` | P4 |
| `bubble` | `CpegoBubble \| None` | สร้างใน `__init__` = `None` | P4 |
| `confirm` | `ConfirmDialog \| None` | สร้างใน `__init__` = `None` | "ถ้าหยุดตอนนี้ ทุกคนได้ผลเดียวกัน" |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `on_enter()` | `None` | ทำตาม class แม่ |
| `on_leave()` | `None` | ทำตาม class แม่ |
| `on_tick(elapsed_sec: int)` | `None` | เหมือน FocusView แต่ใช้ members.set_egg_odds |
| `ask_stop()` | `None` | ทำตาม class แม่ |
| `confirm_stop()` | `None` | ctx.rooms.stop · FAILED → /result (room_id) · READY → /hatch (room_id) |

## Method ที่ต้องเขียนในไฟล์ของคนอื่น

ตัวแปรของ class เหล่านี้ P1 สร้างไว้แล้ว ให้เพิ่มเฉพาะ method ข้างล่าง

### `GroupRoom`

- **ไฟล์:** `app/domain/group_room.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **หน้าที่:** ห้องอ่านกลุ่ม · P1 สร้างตัวแปร + to_dict/from_dict · P5 เขียน method ที่เหลือ

| method | return | ทำอะไร |
|---|---|---|
| `stop(ended_at: datetime, duration_sec: int, min_success_sec: int)` | `RoomStatus` | บันทึกเวลา แล้วเปลี่ยนเป็น FAILED หรือ READY_TO_HATCH |
| `can_hatch()` | `bool` | True ถ้า READY_TO_HATCH |
| `mark_hatched(tier: EggTier)` | `None` | บันทึกระดับไข่ เปลี่ยนเป็น HATCHED |
| `to_dto(members: list[PlayerDTO])` | `RoomDTO` | แปลงเป็น RoomDTO |

## เช็กลิสต์ก่อนส่ง PR

- [ ] create_room สมาชิก 1 คน หรือ 7 คน → ValidationError
- [ ] create_room ที่มีสมาชิก RUNNING อยู่ → InvalidStateError
- [ ] stop ก่อน 15 นาที → ทุก session FAILED
- [ ] hatch → ทุกคนได้ tier เดียวกัน และได้ HatchResult ครบทุกคน
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
