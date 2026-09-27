# F2 · Focus UI (Frontend)

popup ใส่วิชา, หน้า Focus, นาฬิกา, CPEGO, ตารางโอกาสไข่

> อ่าน [00-shared.md](00-shared.md) ก่อน: วิธีทำงานแบบแยกฝั่ง, กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **ฝั่ง:** Frontend อย่างเดียว · เรียก backend ผ่าน `ctx.<service>` เท่านั้น
- **Class ที่ต้องเขียน (8):** `EggOddsPanel`, `StopwatchTimer`, `CpegoMessage`, `CpegoBot`, `CpegoBubble`, `EggView`, `SetupPopup`, `FocusView`
- **ใช้ของใคร:** F1 (ของกลางหน้าจอ) · เรียก `ctx.focus` (B3), `ctx.tiers` (B2)
- **ใครใช้ของเรา:** F3 ใช้นาฬิกา, CPEGO, ตารางโอกาสในห้องกลุ่ม · F4 เปิด `SetupPopup` จาก Lobby
- **branch:** `feat/f2-focus-ui`

## Frontend

**Import ที่ต้องใช้ (รวมทุกไฟล์ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

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

if TYPE_CHECKING:
    from ui.core.app_context import AppContext
```

### `EggOddsPanel`

- **ไฟล์:** `ui/hatch/egg_odds_panel.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `EggOddsPanel(brackets, current_sec=0)`
- **หน้าที่:** ตารางโอกาสได้ไข่ตามเวลา (ใช้ใน popup Setup และหน้า Focus) highlight แถวของเวลาปัจจุบัน

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `brackets` | `list[TierOdds]` | ต้องส่งตอนสร้าง | จาก ctx.tiers.list_odds() |
| `current_sec` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `0` | เวลาที่อ่านแล้ว |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `set_current(duration_sec: int)` | `None` | เปลี่ยนแถวที่ highlight |

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
| `odds_panel` | `EggOddsPanel \| None` | สร้างใน `__init__` = `None` | F2 |

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
| `timer` | `StopwatchTimer \| None` | สร้างใน `__init__` = `None` | นาฬิกา (F2) |
| `time_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความเวลา 67:07 |
| `egg_view` | `EggView \| None` | สร้างใน `__init__` = `None` | รูปไข่ |
| `odds_panel` | `EggOddsPanel \| None` | สร้างใน `__init__` = `None` | F2 |
| `bot` | `CpegoBot \| None` | สร้างใน `__init__` = `None` | CPEGO bot (F2) |
| `bubble` | `CpegoBubble \| None` | สร้างใน `__init__` = `None` | CPEGO bubble (F2) |
| `confirm` | `ConfirmDialog \| None` | สร้างใน `__init__` = `None` | Are you sure to stop? |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `on_enter()` | `None` | โหลด session → timer.start → bubble greeting |
| `on_leave()` | `None` | timer.stop |
| `on_tick(elapsed_sec: int)` | `None` | time_text = Format.clock · egg_view.set_odds · odds_panel.set_current · bot.check → bubble.show |
| `ask_stop()` | `None` | เปิด ConfirmDialog |
| `confirm_stop()` | `None` | ctx.focus.stop · FAILED → /result · READY_TO_HATCH → /hatch (session_id) |

## เช็กลิสต์ก่อนส่ง PR

- [ ] กด START ไม่ใส่วิชา → error_text ขึ้นสีแดง
- [ ] นาฬิกาเดิน และ CPEGO พูดครั้งเดียวต่อช่วงเวลา
- [ ] STOP ก่อน 15 นาที → ไป /result · หลัง 15 นาที → ไป /hatch
- [ ] ออกจากหน้า Focus แล้ว timer หยุด
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
