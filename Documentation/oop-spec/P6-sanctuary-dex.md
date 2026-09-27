# P6 · Sanctuary + Dex

ห้องภาคที่สัตว์เดินไปมา, สมุดสะสม CPE Dex

> อ่าน [00-shared.md](00-shared.md) ก่อน: กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **Backend (2 class):** `SanctuaryService`, `DexService`
- **Frontend (6 class):** `PetSprite`, `SanctuaryScene`, `LobbyView`, `DexCard`, `DexDetailPanel`, `DexView`
- **ใช้ของใคร:** P1 (`GameStore`), P2 (ของกลางหน้าจอ, `HowToPopup`, `StatTile`), P3 (`PetLevelPolicy`, `OwnedPet.to_dto`), P4 (`SetupPopup`)
- **ใครใช้ของเรา:** หน้า Lobby เป็นหน้าที่ทุกหน้ากลับมา
- **branch:** `feat/sanctuary-dex`

## Backend

**Import ที่ต้องใช้ (รวมทุกไฟล์ backend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from app.data.game_store import GameStore
from app.domain.enums import EggTier, Rarity
from app.domain.pet_policy import PetLevelPolicy
from app.dto import DexEntry, PetDTO
from app.errors import NotFoundError
```

### `SanctuaryService`

- **ไฟล์:** `app/services/sanctuary_service.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `SanctuaryService(store)`
- **หน้าที่:** สัตว์ของผู้เล่นไปโชว์ในห้องภาค

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` | P3 |

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

## Frontend

**Import ที่ต้องใช้ (รวมทุกไฟล์ frontend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from typing import Any, Callable, ClassVar, TYPE_CHECKING
import asyncio
import random

import flet as ft

from app.dto import DexEntry, PetDTO, SessionDTO
from ui.core.base_view import BaseView
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.widgets import PixelButton, StatTile
from ui.focus.setup_popup import SetupPopup
from ui.landing.howto_popup import HowToPopup

if TYPE_CHECKING:
    from ui.core.app_context import AppContext
```

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
| `setup` | `SetupPopup \| None` | สร้างใน `__init__` = `None` | P4 |
| `howto` | `HowToPopup \| None` | สร้างใน `__init__` = `None` | P2 |

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

- [ ] list_pets ผู้เล่นที่ยังไม่มีสัตว์ → []
- [ ] list_entries ครบทุกชนิดใน species.json
- [ ] completion ถูกต้องเมื่อมี 3 จาก 12 → 0.25
- [ ] get_entry ได้ subjects ไม่ซ้ำ
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
