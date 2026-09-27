# P7 · Analytics

สรุปผลรายรอบ, ประวัติ, สถิติรวม

> อ่าน [00-shared.md](00-shared.md) ก่อน: กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **Backend (2 class):** `StatsCalculator`, `AnalyticsService`
- **Frontend (4 class):** `ResultCard`, `ResultView`, `BarChart`, `HistoryView`
- **ใช้ของใคร:** P1 (`GameStore`), P2 (ของกลางหน้าจอ, `StatTile`, `Format`), P3 (`PetLevelPolicy`, `OwnedPet.to_dto`)
- **ใครใช้ของเรา:** ปลายทางของทุกรอบการเล่น · หน้า Dex (P6) ใช้วิชาจาก session
- **branch:** `feat/analytics`

## Backend

**Import ที่ต้องใช้ (รวมทุกไฟล์ backend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from datetime import date
from typing import ClassVar

from app.config import Settings
from app.data.game_store import GameStore
from app.domain.enums import EggTier, SessionStatus
from app.domain.pet_policy import PetLevelPolicy
from app.dto import History, HistoryStats, SessionReport
from app.errors import InvalidStateError
```

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
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` | P3 |
| `calculator` | `StatsCalculator` | สร้างใน `__init__` = `StatsCalculator()` | ตัวคำนวณสถิติ |

| method | return | ทำอะไร |
|---|---|---|
| `session_report(session_id: int)` | `SessionReport` | RUNNING หรือ READY_TO_HATCH → InvalidStateError · remaining_sec = max(0, min_success − duration) |
| `room_reports(room_id: int)` | `list[SessionReport]` | report ของสมาชิกทุกคน |
| `history(player_id: int)` | `History` | ทุกรอบที่จบแล้วของผู้เล่น + stats |

## Frontend

**Import ที่ต้องใช้ (รวมทุกไฟล์ frontend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from datetime import date
from typing import Any, Callable, ClassVar, TYPE_CHECKING

import flet as ft

from app.dto import History, SessionReport
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.widgets import PixelButton, StatTile

if TYPE_CHECKING:
    from ui.core.app_context import AppContext
```

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

- [ ] session_report ของรอบ FAILED ได้ remaining_sec ถูก
- [ ] session_report ของรอบ RUNNING → InvalidStateError
- [ ] StatsCalculator.success_rate ของ 0 รอบ = 0.0
- [ ] daily_study_sec มีครบ 7 วัน วันที่ไม่ได้อ่าน = 0
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
