# F3 · Room + Result UI (Frontend)

หน้าตั้งห้องกลุ่ม, หน้าอ่านกลุ่ม, หน้า Result, หน้า History

> อ่าน [00-shared.md](00-shared.md) ก่อน: วิธีทำงานแบบแยกฝั่ง, กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **ฝั่ง:** Frontend อย่างเดียว · เรียก backend ผ่าน `ctx.<service>` เท่านั้น
- **Class ที่ต้องเขียน (8):** `MemberPicker`, `RoomSetupView`, `MemberList`, `RoomFocusView`, `ResultCard`, `ResultView`, `BarChart`, `HistoryView`
- **ใช้ของใคร:** F1 (ของกลางหน้าจอ, `StatTile`, `Format`) · F2 (`StopwatchTimer`, `CpegoBot`, `CpegoBubble`, `EggOddsPanel`) · เรียก `ctx.rooms`, `ctx.analytics`, `ctx.players`
- **ใครใช้ของเรา:** ปลายทางของทุกรอบการเล่น (Result) · Lobby (F4) เปิดหน้าห้องกลุ่มและ History
- **branch:** `feat/f3-room-result-ui`

## Frontend

**Import ที่ต้องใช้ (รวมทุกไฟล์ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from datetime import date
from typing import Any, Callable, ClassVar, TYPE_CHECKING

import flet as ft

from app.domain.enums import EggTier, RoomStatus
from app.dto import History, PlayerDTO, RoomDTO, SessionReport
from app.errors import AppError, ValidationError
from ui.core.base_view import BaseView
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.widgets import ConfirmDialog, PixelButton, StatTile
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
| `timer` | `StopwatchTimer \| None` | สร้างใน `__init__` = `None` | F2 |
| `time_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความเวลา 67:07 |
| `members` | `MemberList \| None` | สร้างใน `__init__` = `None` | สมาชิก |
| `odds_panel` | `EggOddsPanel \| None` | สร้างใน `__init__` = `None` | F2 |
| `bot` | `CpegoBot \| None` | สร้างใน `__init__` = `None` | F2 |
| `bubble` | `CpegoBubble \| None` | สร้างใน `__init__` = `None` | F2 |
| `confirm` | `ConfirmDialog \| None` | สร้างใน `__init__` = `None` | "ถ้าหยุดตอนนี้ ทุกคนได้ผลเดียวกัน" |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `on_enter()` | `None` | ทำตาม class แม่ |
| `on_leave()` | `None` | ทำตาม class แม่ |
| `on_tick(elapsed_sec: int)` | `None` | เหมือน FocusView แต่ใช้ members.set_egg_odds |
| `ask_stop()` | `None` | ทำตาม class แม่ |
| `confirm_stop()` | `None` | ctx.rooms.stop · FAILED → /result (room_id) · READY → /hatch (room_id) |

### `ResultCard`

- **ไฟล์:** `ui/result/result_card.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `ResultCard(report, nickname)`
- **หน้าที่:** การ์ดสรุปหนึ่งคน: สำเร็จ = ไข่ที่ได้ + สัตว์ + ตัวใหม่/level up · ไม่สำเร็จ = ต้องอ่านอีกกี่นาที

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `report` | `SessionReport` | ต้องส่งตอนสร้าง | ข้อมูลสรุป |
| `nickname` | `str` | ต้องส่งตอนสร้าง | ชื่อผู้เล่น (โชว์ในห้องกลุ่ม) |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | เลือก _build_success / _build_failed |
| `_build_success()` *private* | `ft.Control` | ทำตาม class แม่ |
| `_build_failed()` *private* | `ft.Control` | ทำตาม class แม่ |

### `ResultView`

- **ไฟล์:** `ui/result/result_view.py`
- **ชนิด:** class
- **inherit:** `BaseView`
- **สร้าง:** `ResultView(ctx, **params)`
- **หน้าที่:** หน้า Result: การ์ด 1 ใบ (เดี่ยว) หรือหลายใบ (กลุ่ม) + RETURN TO LOBBY

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/result"` | path ของหน้า |
| `reports` | `list[SessionReport]` | สร้างใน `__init__` = `[]` | ทุก report |
| `cards` | `list[ResultCard]` | สร้างใน `__init__` = `[]` | การ์ดทุกใบ |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `on_enter()` | `None` | session_id → session_report · room_id → room_reports |
| `return_to_lobby()` | `None` | ทำตาม class แม่ |

### `BarChart`

- **ไฟล์:** `ui/result/bar_chart.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `BarChart(values, format_value, bar_height=160)`
- **หน้าที่:** กราฟแท่งวาดด้วย Container (ไม่ต้องลง library กราฟ)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `values` | `dict[str, int]` | ต้องส่งตอนสร้าง | label → ค่า |
| `format_value` | `Callable[[int], str]` | ต้องส่งตอนสร้าง | เช่น Format.duration |
| `bar_height` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `160` | px แท่งสูงสุด |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ความสูงแต่ละแท่ง = value / max × bar_height |

### `HistoryView`

- **ไฟล์:** `ui/result/history_view.py`
- **ชนิด:** class
- **inherit:** `BaseView`
- **สร้าง:** `HistoryView(ctx, **params)`
- **หน้าที่:** หน้า History: StatTile (รอบทั้งหมด, อัตราสำเร็จ, เวลารวม), กราฟ 7 วัน, กราฟแยกวิชา, ไข่แต่ละระดับ, รายการทุกรอบ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/history"` | path ของหน้า |
| `history` | `History \| None` | สร้างใน `__init__` = `None` | ข้อมูล History |
| `daily_chart` | `BarChart \| None` | สร้างใน `__init__` = `None` | กราฟ 7 วัน |
| `subject_chart` | `BarChart \| None` | สร้างใน `__init__` = `None` | กราฟแยกวิชา |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `on_enter()` | `None` | ctx.analytics.history(player.id) |
| `render_row(report: SessionReport)` | `ft.Control` | หนึ่งแถว: วันที่, วิชา, เวลา, ผล |
| `open_report(session_id: int)` | `None` | ไป /result |
| `close()` | `None` | ไป /lobby |

## เช็กลิสต์ก่อนส่ง PR

- [ ] ตั้งห้องสมาชิก 1 คน → ขึ้น error
- [ ] STOP ห้องกลุ่ม → ไป /hatch หรือ /result พร้อม room_id
- [ ] หน้า Result โชว์การ์ดครบทุกคนในห้อง
- [ ] หน้า History กราฟ 7 วันไม่ล้นจอมือถือ
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
