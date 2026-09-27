# P4 · Study Timer

การอ่านเดี่ยว, นาฬิกา, หน้า Focus, CPEGO bubble

> อ่าน [00-shared.md](00-shared.md) ก่อน: กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **Backend (1 class):** `FocusSessionService`
- **Frontend (7 class):** `StopwatchTimer`, `CpegoMessage`, `CpegoBot`, `CpegoBubble`, `EggView`, `SetupPopup`, `FocusView`
- **method ในไฟล์ของคนอื่น:** `StudySession`
- **ใช้ของใคร:** P1 (`GameStore`, `Clock`, `StudySession`), P2 (`BaseView`, `BaseWidget`, `Popup`, `ConfirmDialog`, `Format`), P3 (`TierOddsTable`, `EggOddsPanel`)
- **ใครใช้ของเรา:** P5 ใช้ `StopwatchTimer`, `CpegoBot`, `CpegoBubble` ในห้องกลุ่ม · P6 เปิด `SetupPopup` จาก Lobby · P3 ใช้ `can_hatch()`, `mark_hatched()`
- **branch:** `feat/study-timer`

## Backend

**Import ที่ต้องใช้ (รวมทุกไฟล์ backend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from app.config import Settings
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.domain.enums import SessionStatus
from app.domain.study_session import StudySession
from app.domain.tier_odds_table import TierOddsTable
from app.dto import SessionDTO, StopResult
from app.errors import InvalidStateError, ValidationError
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

## Frontend

**Import ที่ต้องใช้ (รวมทุกไฟล์ frontend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, ClassVar, TYPE_CHECKING
import asyncio

import flet as ft

from app.core.clock import Clock
from app.domain.enums import EggTier, SessionStatus
from app.dto import SessionDTO, TierOdds
from app.errors import AppError, ValidationError
from ui.core.base_view import BaseView
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.widgets import ConfirmDialog, PixelButton, Popup
from ui.hatch.egg_odds_panel import EggOddsPanel

if TYPE_CHECKING:
    from ui.core.app_context import AppContext
```

### `StopwatchTimer`

- **ไฟล์:** `ui/focus/stopwatch_timer.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `StopwatchTimer(clock, started_at, on_tick, interval_sec=1.0)`
- **หน้าที่:** นาฬิกานับขึ้น ทุก interval_sec คำนวณเวลาใหม่จาก started_at แล้วเรียก on_tick

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `clock` | `Clock` | ต้องส่งตอนสร้าง | นาฬิกากลาง |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `on_tick` | `Callable[[int], None]` | ต้องส่งตอนสร้าง | เรียกทุก tick พร้อม elapsed_sec |
| `interval_sec` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1.0` | ระยะห่างแต่ละ tick (วินาที) |
| `running` | `bool` | สร้างใน `__init__` = `False` | ทำงานอยู่ไหม |

| method | return | ทำอะไร |
|---|---|---|
| `start(page: ft.Page)` | `None` | running = True แล้ว page.run_task(_loop) |
| `stop()` | `None` | running = False |
| `elapsed_sec` *@property* | `int` | clock.elapsed_sec(started_at) |
| `_loop()` *private* | `None` | async: while running → on_tick(elapsed_sec) → await asyncio.sleep(interval_sec) |

### `CpegoMessage`

- **ไฟล์:** `ui/focus/cpego_bot.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `CpegoMessage(text=...)`
- **หน้าที่:** ข้อความหนึ่งอันของ CPEGO

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `text` | `str` | ต้องส่งตอนสร้าง | ข้อความ |
| `kind` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"info"` | "greeting" \| "milestone" \| "info" |

### `CpegoBot`

- **ไฟล์:** `ui/focus/cpego_bot.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `CpegoBot(brackets)`
- **หน้าที่:** ตัดสินว่า CPEGO ต้องพูดอะไรเมื่อไหร่ (พูดครั้งเดียวต่อช่วงเวลา)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `brackets` | `list[TierOdds]` | ต้องส่งตอนสร้าง | จาก ctx.tiers.list_odds() ใช้ min_minutes เป็น milestone |
| `_announced` | `set[int]` | สร้างใน `__init__` = `set()` | min_minutes ที่พูดไปแล้ว |

| method | return | ทำอะไร |
|---|---|---|
| `greeting(subject: str)` | `CpegoMessage` | ทักตอนเริ่ม |
| `check(elapsed_sec: int)` | `CpegoMessage \| None` | เพิ่งเข้าช่วงใหม่ (elapsed_sec >= min_minutes × 60) และยังไม่พูด → ข้อความเช่น "ครบ 30 นาที! ตอนนี้มีสิทธิ์ลุ้นไข่อาจารย์ 10%" |
| `reset()` | `None` | ทำตาม class แม่ |

### `CpegoBubble`

- **ไฟล์:** `ui/focus/cpego_bubble.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `CpegoBubble(show_sec=5.0)`
- **หน้าที่:** bubble CPEGO เด้งมุมจอแล้วหายเอง

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `show_sec` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `5.0` | โชว์กี่วินาที |
| `visible` | `bool` | สร้างใน `__init__` = `False` | - |
| `text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความ |
| `_hide_token` | `int` | สร้างใน `__init__` = `0` | นับครั้งที่ show ใช้กันงานซ่อนเก่ามาซ่อนข้อความใหม่ |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | รูป CPEGO + กล่องข้อความ |
| `show(page: ft.Page, message: CpegoMessage)` | `None` | โชว์ แล้วตั้งเวลาซ่อนด้วย page.run_task |
| `hide()` | `None` | ทำตาม class แม่ |

### `EggView`

- **ไฟล์:** `ui/focus/egg_view.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `EggView(odds=None)`
- **หน้าที่:** รูปไข่กลางจอ + แถบโอกาสไข่ตามเวลาปัจจุบัน

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `odds` | `dict[EggTier, int]` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `{}` | โอกาสตอนนี้ ว่าง = ยังไม่ถึง 15 นาที |
| `image` | `ft.Image \| None` | สร้างใน `__init__` = `None` | รูป |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `set_odds(odds: dict[EggTier, int])` | `None` | เปลี่ยนรูปไข่ (ไข่เรืองแสงมากขึ้นตามโอกาสไข่อาจารย์) |
| `wobble()` | `None` | ไข่ขยับตอนเข้าช่วงใหม่ |

### `SetupPopup`

- **ไฟล์:** `ui/focus/setup_popup.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `SetupPopup(ctx, on_started, on_back)`
- **หน้าที่:** popup หลังกด START FOCUS: ชื่อวิชา, วิชาล่าสุด, ตาราง EggOddsPanel, START / BACK

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `ctx` | `AppContext` | ต้องส่งตอนสร้าง | ของกลาง |
| `on_started` | `Callable[[SessionDTO], None]` | ต้องส่งตอนสร้าง | เริ่มสำเร็จ |
| `on_back` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กด BACK |
| `subject_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` | ช่องชื่อวิชา |
| `error_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความเตือนสีแดง |
| `odds_panel` | `EggOddsPanel \| None` | สร้างใน `__init__` = `None` | P3 |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `subject` *@property* | `str` | ชื่อวิชา ตัดช่องว่างแล้ว |
| `start()` | `None` | ctx.focus.start(ctx.player.id, subject) → on_started · ValidationError → error_text |

### `FocusView`

- **ไฟล์:** `ui/focus/focus_view.py`
- **ชนิด:** class
- **inherit:** `BaseView`
- **สร้าง:** `FocusView(ctx, **params)`
- **หน้าที่:** หน้า Focus (อ่านเดี่ยว): นาฬิกา, ไข่, ตารางโอกาส, CPEGO bubble, STOP

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/focus"` | path ของหน้า |
| `session` | `SessionDTO \| None` | สร้างใน `__init__` = `None` | params["session_id"] |
| `timer` | `StopwatchTimer \| None` | สร้างใน `__init__` = `None` | นาฬิกา (P4) |
| `time_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความเวลา 67:07 |
| `egg_view` | `EggView \| None` | สร้างใน `__init__` = `None` | รูปไข่ |
| `odds_panel` | `EggOddsPanel \| None` | สร้างใน `__init__` = `None` | P3 |
| `bot` | `CpegoBot \| None` | สร้างใน `__init__` = `None` | CPEGO bot (P4) |
| `bubble` | `CpegoBubble \| None` | สร้างใน `__init__` = `None` | CPEGO bubble (P4) |
| `confirm` | `ConfirmDialog \| None` | สร้างใน `__init__` = `None` | Are you sure to stop? |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `on_enter()` | `None` | โหลด session → timer.start → bubble greeting |
| `on_leave()` | `None` | timer.stop |
| `on_tick(elapsed_sec: int)` | `None` | time_text = Format.clock · egg_view.set_odds · odds_panel.set_current · bot.check → bubble.show |
| `ask_stop()` | `None` | เปิด ConfirmDialog |
| `confirm_stop()` | `None` | ctx.focus.stop · FAILED → /result · READY_TO_HATCH → /hatch (session_id) |

## Method ที่ต้องเขียนในไฟล์ของคนอื่น

ตัวแปรของ class เหล่านี้ P1 สร้างไว้แล้ว ให้เพิ่มเฉพาะ method ข้างล่าง

### `StudySession`

- **ไฟล์:** `app/domain/study_session.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **หน้าที่:** การอ่านหนึ่งรอบของผู้เล่นหนึ่งคน · P1 สร้างตัวแปร + to_dict/from_dict · P4 เขียน method ที่เหลือ (เปลี่ยน status ผ่าน method เท่านั้น)

| method | return | ทำอะไร |
|---|---|---|
| `stop(ended_at: datetime, duration_sec: int, min_success_sec: int)` | `SessionStatus` | บันทึกเวลา แล้วเปลี่ยนเป็น FAILED หรือ READY_TO_HATCH · ไม่ได้ RUNNING → InvalidStateError |
| `can_hatch()` | `bool` | True ถ้า READY_TO_HATCH |
| `mark_hatched(tier: EggTier, species_code: str)` | `None` | บันทึกไข่ + สัตว์ แล้วเปลี่ยนเป็น HATCHED · ไม่ได้ READY_TO_HATCH → InvalidStateError |
| `is_running()` | `bool` | True ถ้า RUNNING |
| `is_success()` | `bool` | True ถ้า HATCHED |
| `to_dto()` | `SessionDTO` | แปลงเป็น SessionDTO |

## เช็กลิสต์ก่อนส่ง PR

- [ ] start ชื่อวิชาว่าง → ValidationError
- [ ] start ตอนมี RUNNING อยู่ → InvalidStateError
- [ ] stop ก่อน 15 นาที → FAILED, tier_odds ว่าง
- [ ] stop หลัง 30 นาที → READY_TO_HATCH, tier_odds = 55/35/10
- [ ] CpegoBot.check พูดครั้งเดียวต่อช่วง
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
