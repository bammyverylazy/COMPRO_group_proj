# F4 · Lobby, Dex + Hatch UI (Frontend)

หน้า Lobby สัตว์เดิน, หน้า Dex, หน้าฟักไข่ + animation

> อ่าน [00-shared.md](00-shared.md) ก่อน: วิธีทำงานแบบแยกฝั่ง, กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **ฝั่ง:** Frontend อย่างเดียว · เรียก backend ผ่าน `ctx.<service>` เท่านั้น
- **Class ที่ต้องเขียน (8):** `HatchAnimation`, `HatchView`, `PetSprite`, `SanctuaryScene`, `LobbyView`, `DexCard`, `DexDetailPanel`, `DexView`
- **ใช้ของใคร:** F1 (ของกลางหน้าจอ, `HowToPopup`) · F2 (`SetupPopup`) · เรียก `ctx.sanctuary`, `ctx.dex`, `ctx.hatch`, `ctx.rooms.hatch`, `ctx.focus.get_running`
- **ใครใช้ของเรา:** หน้า Lobby เป็นหน้าที่ทุกหน้ากลับมา · Focus (F2) และ Room (F3) ส่งมาหน้าฟักไข่
- **branch:** `feat/f4-lobby-dex-hatch-ui`

## Frontend

**Import ที่ต้องใช้ (รวมทุกไฟล์ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from typing import Any, Callable, ClassVar, TYPE_CHECKING
import asyncio
import random

import flet as ft

from app.domain.enums import EggTier
from app.dto import DexEntry, HatchResult, PetDTO, SessionDTO
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.widgets import PixelButton, StatTile
from ui.focus.setup_popup import SetupPopup
from ui.landing.howto_popup import HowToPopup

if TYPE_CHECKING:
    from ui.core.app_context import AppContext
```

### `HatchAnimation`

- **ไฟล์:** `ui/hatch/hatch_animation.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `HatchAnimation(tier, pet, stage_ms=900)`
- **หน้าที่:** animation: ไข่ 3 ใบวนสุ่ม → หยุดที่ระดับที่ได้ → สั่น → แตก → TADA

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ระดับที่สุ่มได้ |
| `pet` | `PetDTO` | ต้องส่งตอนสร้าง | สัตว์ที่ได้ |
| `STAGES` | `tuple[str, ...]` | ค่าคงที่ของ class `= ("roulette", "shake", "crack", "reveal")` | - |
| `stage_ms` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `900` | เวลาต่อขั้น |
| `current_stage` | `int` | สร้างใน `__init__` = `0` | - |
| `stack` | `ft.Stack \| None` | สร้างใน `__init__` = `None` | ft.Stack ที่วางของ |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `play(page: ft.Page, on_done: Callable[[], None])` | `None` | เล่นทีละขั้นด้วย page.run_task จบแล้ว on_done |
| `skip()` | `None` | ข้ามไปขั้นสุดท้าย |

### `HatchView`

- **ไฟล์:** `ui/hatch/hatch_view.py`
- **ชนิด:** class
- **inherit:** `BaseView`
- **สร้าง:** `HatchView(ctx, **params)`
- **หน้าที่:** หน้าฟักไข่ params: session_id (อ่านเดี่ยว) หรือ room_id (กลุ่ม) · จบแล้วไป /result

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/hatch"` | path ของหน้า |
| `results` | `list[HatchResult]` | สร้างใน `__init__` = `[]` | ผลของทุกคน (เดี่ยว = 1) |
| `current_index` | `int` | สร้างใน `__init__` = `0` | กำลังโชว์ของคนที่เท่าไร |
| `animation` | `HatchAnimation \| None` | สร้างใน `__init__` = `None` | animation ฟักไข่ |
| `name_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | Congrats! {nickname} got {species} |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `on_enter()` | `None` | session_id → ctx.hatch.hatch · room_id → ctx.rooms.hatch แล้ว play_current |
| `play_current()` | `None` | เล่น animation ของคนที่ current_index + sound.play("tada") |
| `next()` | `None` | คนถัดไป ถ้าหมดแล้ว go_result |
| `go_result()` | `None` | ไป /result พร้อม session_id หรือ room_id |

### `PetSprite`

- **ไฟล์:** `ui/lobby/pet_sprite.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `PetSprite(pet, x, y, speed=40.0)`
- **หน้าที่:** สัตว์หนึ่งตัวในห้อง เดินไปจุดสุ่ม หยุดพัก แล้วสุ่มใหม่

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `pet` | `PetDTO` | ต้องส่งตอนสร้าง | สัตว์ |
| `x` | `float` | ต้องส่งตอนสร้าง | ตำแหน่งแนวนอน (px) |
| `y` | `float` | ต้องส่งตอนสร้าง | ตำแหน่งแนวตั้ง (px) |
| `BASE_SIZE` | `int` | ค่าคงที่ของ class `= 64` | px ตอน level 1 |
| `speed` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `40.0` | px ต่อวินาที |
| `target_x` | `float` | สร้างใน `__init__` = `x` | - |
| `target_y` | `float` | สร้างใน `__init__` = `y` | จุดที่กำลังเดินไป |
| `rest_sec` | `float` | สร้างใน `__init__` = `0.0` | เหลือเวลาพัก |
| `facing_left` | `bool` | สร้างใน `__init__` = `False` | - |
| `image` | `ft.Image \| None` | สร้างใน `__init__` = `None` | รูป |

| method | return | ทำอะไร |
|---|---|---|
| `size` *@property* | `float` | BASE_SIZE × pet.scale |
| `build()` | `ft.Control` | ft.Image วางด้วย left/top |
| `choose_target(width: float, height: float)` | `None` | สุ่มจุดใหม่ด้วย random.uniform |
| `update(dt: float, width: float, height: float)` | `None` | ขยับตาม speed ถึงแล้วพัก 1–3 วิ |

### `SanctuaryScene`

- **ไฟล์:** `ui/lobby/sanctuary_scene.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `SanctuaryScene(width, height, fps=20)`
- **หน้าที่:** ฉากห้องภาค: พื้นหลัง + สัตว์ทุกตัว

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `width` | `float` | ต้องส่งตอนสร้าง | กว้าง (px) |
| `height` | `float` | ต้องส่งตอนสร้าง | สูง (px) |
| `fps` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `20` | อัปเดตต่อวินาที |
| `sprites` | `list[PetSprite]` | สร้างใน `__init__` = `[]` | สัตว์ในห้อง |
| `running` | `bool` | สร้างใน `__init__` = `False` | ทำงานอยู่ไหม |
| `stack` | `ft.Stack \| None` | สร้างใน `__init__` = `None` | ft.Stack ที่วางของ |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `load(pets: list[PetDTO])` | `None` | สร้าง PetSprite วางตำแหน่งสุ่ม |
| `start(page: ft.Page)` | `None` | page.run_task(_loop) |
| `stop()` | `None` | ทำตาม class แม่ |
| `_loop()` *private* | `None` | async: while running → tick(1 / fps) → await asyncio.sleep(1 / fps) |
| `tick(dt: float)` | `None` | update ทุก sprite แล้ว refresh |

### `LobbyView`

- **ไฟล์:** `ui/lobby/lobby_view.py`
- **ชนิด:** class
- **inherit:** `BaseView`
- **สร้าง:** `LobbyView(ctx, **params)`
- **หน้าที่:** หน้า Lobby: ห้องภาค + ปุ่ม START FOCUS, GROUP STUDY, DEX, HISTORY, HOW TO, เปลี่ยนผู้เล่น (ห้องว่างโชว์ข้อความชวนเริ่มอ่าน)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/lobby"` | path ของหน้า |
| `scene` | `SanctuaryScene \| None` | สร้างใน `__init__` = `None` | ฉากห้องภาค |
| `setup` | `SetupPopup \| None` | สร้างใน `__init__` = `None` | F2 |
| `howto` | `HowToPopup \| None` | สร้างใน `__init__` = `None` | F1 |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `on_enter()` | `None` | ถ้ามี session RUNNING ค้างไป /focus เลย · ไม่มี → list_pets → scene.start |
| `on_leave()` | `None` | scene.stop |
| `start_focus()` | `None` | เปิด SetupPopup |
| `on_session_started(session: SessionDTO)` | `None` | ไป /focus (session_id) |
| `start_group()` | `None` | ไป /room/setup |
| `open_dex()` | `None` | ไป /dex |
| `open_history()` | `None` | ไป /history |
| `open_howto()` | `None` | ทำตาม class แม่ |
| `switch_player()` | `None` | ctx.player = None แล้วไป / |

### `DexCard`

- **ไฟล์:** `ui/dex/dex_card.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `DexCard(entry, on_select, selected=False)`
- **หน้าที่:** ช่องหนึ่งใน grid ยังไม่ปลดล็อก = เงาดำ + "???"

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `entry` | `DexEntry` | ต้องส่งตอนสร้าง | ข้อมูลช่องนี้ |
| `on_select` | `Callable[[DexEntry], None]` | ต้องส่งตอนสร้าง | กดเลือก |
| `selected` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `False` | ถูกเลือกอยู่ |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `set_selected(selected: bool)` | `None` | ทำตาม class แม่ |

### `DexDetailPanel`

- **ไฟล์:** `ui/dex/dex_detail_panel.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `DexDetailPanel(entry=None)`
- **หน้าที่:** panel รายละเอียด: รูปใหญ่, ชื่อ, tier, rarity, level, ได้ครั้งแรก, วิชาที่อ่าน

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `entry` | `DexEntry \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ข้อมูลช่องนี้ |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `show(entry: DexEntry)` | `None` | ทำตาม class แม่ |

### `DexView`

- **ไฟล์:** `ui/dex/dex_view.py`
- **ชนิด:** class
- **inherit:** `BaseView`
- **สร้าง:** `DexView(ctx, **params)`
- **หน้าที่:** หน้า CPE Dex: % สะสม, grid แยกตาม tier, panel รายละเอียด, ปุ่มกลับ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/dex"` | path ของหน้า |
| `entries` | `list[DexEntry]` | สร้างใน `__init__` = `[]` | ทุกช่องใน Dex |
| `cards` | `list[DexCard]` | สร้างใน `__init__` = `[]` | การ์ดทุกใบ |
| `detail` | `DexDetailPanel \| None` | สร้างใน `__init__` = `None` | panel รายละเอียด |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `on_enter()` | `None` | list_entries + completion |
| `select(entry: DexEntry)` | `None` | highlight + detail.show |
| `close()` | `None` | ไป /lobby |

## เช็กลิสต์ก่อนส่ง PR

- [ ] ห้องว่างโชว์ข้อความชวนเริ่มอ่าน
- [ ] สัตว์ level สูงตัวใหญ่ขึ้น และเดินไม่ออกนอกห้อง
- [ ] Dex ตัวที่ยังไม่ได้เป็นเงาดำ
- [ ] หน้าฟักไข่ห้องกลุ่มเล่นครบทุกคนแล้วไป /result
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
