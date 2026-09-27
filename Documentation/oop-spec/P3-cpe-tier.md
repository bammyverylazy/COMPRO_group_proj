# P3 · CPE Tier

ไข่ 3 ระดับ, สุ่มระดับไข่ตามเวลา, สุ่มสัตว์, หน้าฟักไข่

> อ่าน [00-shared.md](00-shared.md) ก่อน: กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **Backend (10 class):** `Egg`, `FreshmanEgg`, `SeniorEgg`, `ProfessorEgg`, `EggFactory`, `TierOddsTable`, `GachaMachine`, `PetLevelPolicy`, `TierService`, `HatchService`
- **Frontend (3 class):** `EggOddsPanel`, `HatchAnimation`, `HatchView`
- **method ในไฟล์ของคนอื่น:** `OwnedPet`
- **ใช้ของใคร:** P1 (`GameStore`, `Species`, `OwnedPet`, `StudySession`), P2 (`BaseView`, `BaseWidget`, `Format`, `SoundManager`), P4 (`StudySession.can_hatch`, `mark_hatched`)
- **ใครใช้ของเรา:** P4, P5 ใช้ `EggOddsPanel`, `TierOddsTable` · P5 เรียก `HatchService` · P6, P7 ใช้ `PetLevelPolicy`
- **branch:** `feat/cpe-tier`

## Backend

**Import ที่ต้องใช้ (รวมทุกไฟล์ backend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar
import random

from app.data.game_store import GameStore
from app.domain.enums import EggTier, Rarity
from app.domain.owned_pet import OwnedPet
from app.domain.species import Species
from app.dto import HatchResult, TierInfo, TierOdds
from app.errors import InvalidStateError
```

### `Egg`

- **ไฟล์:** `app/domain/eggs.py`
- **ชนิด:** abstract class
- **inherit:** ไม่มี (เป็น `ABC`)
- **หน้าที่:** แม่ของไข่ทุกระดับ ลูกบอกโอกาสแต่ละ rarity (abstraction + polymorphism)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.FRESHMAN` | ลูก override |
| `name_th` | `str` | ค่าคงที่ของ class `= ""` | ชื่อไทย |
| `image_path` | `str` | ค่าคงที่ของ class `= ""` | รูปไข่ |

| method | return | ทำอะไร |
|---|---|---|
| `rarity_weights()` *abstract* | `dict[Rarity, int]` | โอกาสแต่ละ rarity รวม 100 |
| `roll_species(pool: list[Species], gacha: GachaMachine)` | `Species` | gacha.pick_rarity(rarity_weights()) แล้ว gacha.pick_species |
| `to_tier_info()` | `TierInfo` | แปลงเป็น TierInfo |

### `FreshmanEgg`

- **ไฟล์:** `app/domain/eggs.py`
- **ชนิด:** class
- **inherit:** `Egg`
- **สร้าง:** `FreshmanEgg()`
- **หน้าที่:** ไข่รุ่นเรา · Common 70 / Rare 25 / Epic 5 / Legendary 0

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.FRESHMAN` | ระดับของไข่นี้ |
| `name_th` | `str` | ค่าคงที่ของ class `= "ไข่รุ่นเรา"` | ชื่อไทย |
| `image_path` | `str` | ค่าคงที่ของ class `= "eggs/freshman.png"` | รูปไข่ |

| method | return | ทำอะไร |
|---|---|---|
| `rarity_weights()` *เขียนให้แล้ว* | `dict[Rarity, int]` | 70 / 25 / 5 / 0 |

### `SeniorEgg`

- **ไฟล์:** `app/domain/eggs.py`
- **ชนิด:** class
- **inherit:** `Egg`
- **สร้าง:** `SeniorEgg()`
- **หน้าที่:** ไข่รุ่นพี่ · Common 40 / Rare 40 / Epic 17 / Legendary 3

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.SENIOR` | ระดับของไข่นี้ |
| `name_th` | `str` | ค่าคงที่ของ class `= "ไข่รุ่นพี่"` | ชื่อไทย |
| `image_path` | `str` | ค่าคงที่ของ class `= "eggs/senior.png"` | รูปไข่ |

| method | return | ทำอะไร |
|---|---|---|
| `rarity_weights()` *เขียนให้แล้ว* | `dict[Rarity, int]` | 40 / 40 / 17 / 3 |

### `ProfessorEgg`

- **ไฟล์:** `app/domain/eggs.py`
- **ชนิด:** class
- **inherit:** `Egg`
- **สร้าง:** `ProfessorEgg()`
- **หน้าที่:** ไข่อาจารย์ · Common 10 / Rare 40 / Epic 35 / Legendary 15

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.PROFESSOR` | ระดับของไข่นี้ |
| `name_th` | `str` | ค่าคงที่ของ class `= "ไข่อาจารย์"` | ชื่อไทย |
| `image_path` | `str` | ค่าคงที่ของ class `= "eggs/professor.png"` | รูปไข่ |

| method | return | ทำอะไร |
|---|---|---|
| `rarity_weights()` *เขียนให้แล้ว* | `dict[Rarity, int]` | 10 / 40 / 35 / 15 |

### `EggFactory`

- **ไฟล์:** `app/domain/egg_factory.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `EggFactory()`
- **หน้าที่:** สร้าง Egg จาก EggTier

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_registry` | `dict[EggTier, type[Egg]]` | สร้างใน `__init__` = `{EggTier.FRESHMAN: FreshmanEgg, EggTier.SENIOR: SeniorEgg, EggTier.PROFESSOR: ProfessorEgg}` | tier → class |

| method | return | ทำอะไร |
|---|---|---|
| `create(tier: EggTier)` | `Egg` | ทำตาม class แม่ |
| `all()` | `list[Egg]` | ทุกระดับ ต่ำไปสูง |

### `TierOddsTable`

- **ไฟล์:** `app/domain/tier_odds_table.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `TierOddsTable()`
- **หน้าที่:** ตารางโอกาสได้ไข่แต่ละระดับตามเวลาที่อ่าน ยิ่งอ่านนานยิ่งมีสิทธิ์ลุ้นไข่สูง แต่ไม่การันตี

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `BRACKETS` | `tuple[TierOdds, ...]` | ค่าคงที่ของ class `= (TierOdds(15, 30, {EggTier.FRESHMAN: 85, EggTier.SENIOR: 13, EggTier.PROFESSOR: 2}), TierOdds(30, 60, {EggTier.FRESHMAN: 55, EggTier.SENIOR: 35, EggTier.PROFESSOR: 10}), TierOdds(60, 90, {EggTier.FRESHMAN: 30, EggTier.SENIOR: 45, EggTier.PROFESSOR: 25}), TierOdds(90, None, {EggTier.FRESHMAN: 15, EggTier.SENIOR: 45, EggTier.PROFESSOR: 40}))` | 15–29 → 85/13/2 · 30–59 → 55/35/10 · 60–89 → 30/45/25 · 90+ → 15/45/40 |

| method | return | ทำอะไร |
|---|---|---|
| `bracket_for(duration_sec: int)` | `TierOdds \| None` | ช่วงที่ตรงกับเวลา ต่ำกว่า 15 นาทีคืน None |
| `odds_for(duration_sec: int)` | `dict[EggTier, int]` | weights ของช่วงนั้น ต่ำกว่า 15 นาทีคืน {} |
| `next_bracket(duration_sec: int)` | `TierOdds \| None` | ช่วงถัดไป (ให้ CPEGO บอกว่าอ่านอีกกี่นาทีโอกาสจะดีขึ้น) |
| `all_brackets()` | `list[TierOdds]` | ทุกช่วง ใช้โชว์ตาราง |

### `GachaMachine`

- **ไฟล์:** `app/domain/gacha.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `GachaMachine(seed=None)`
- **หน้าที่:** ตัวสุ่มกลาง ใส่ seed ได้เพื่อให้เทสต์ได้ผลเดิม

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `seed` | `int \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | None = สุ่มจริง |
| `rng` | `random.Random` | สร้างใน `__init__` = `random.Random(seed)` | ตัวสุ่มของ Python |

| method | return | ทำอะไร |
|---|---|---|
| `pick_weighted(weights: dict[Any, int])` | `Any` | สุ่ม key ตามน้ำหนัก ข้าม weight 0 · ว่าง → ValueError |
| `pick_tier(odds: dict[EggTier, int])` | `EggTier` | pick_weighted(odds) |
| `pick_rarity(weights: dict[Rarity, int])` | `Rarity` | pick_weighted(weights) |
| `pick_species(pool: list[Species], rarity: Rarity)` | `Species` | สุ่มจาก pool ที่ rarity ตรง ไม่มีให้ลด rarity ลงทีละขั้น |

### `PetLevelPolicy`

- **ไฟล์:** `app/domain/pet_policy.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `PetLevelPolicy()`
- **หน้าที่:** กติกา level และขนาด

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `SCALE_STEP` | `float` | ค่าคงที่ของ class `= 0.15` | ใหญ่ขึ้นต่อ level |
| `MAX_SCALE` | `float` | ค่าคงที่ของ class `= 2.0` | - |
| `MAX_LEVEL` | `int` | ค่าคงที่ของ class `= 99` | - |

| method | return | ทำอะไร |
|---|---|---|
| `next_level(level: int)` | `int` | min(level + 1, MAX_LEVEL) |
| `scale_for(level: int)` | `float` | min(1 + (level − 1) × SCALE_STEP, MAX_SCALE) |

### `TierService`

- **ไฟล์:** `app/services/tier_service.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `TierService()`
- **หน้าที่:** ข้อมูลไข่ให้หน้าจอ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `factory` | `EggFactory` | สร้างใน `__init__` = `EggFactory()` | สร้างไข่ |
| `odds_table` | `TierOddsTable` | สร้างใน `__init__` = `TierOddsTable()` | ตารางโอกาสไข่ตามเวลา |

| method | return | ทำอะไร |
|---|---|---|
| `list_tiers()` | `list[TierInfo]` | ไข่ทุกระดับ |
| `list_odds()` | `list[TierOdds]` | ตารางโอกาสตามเวลา |
| `odds_for(duration_sec: int)` | `dict[EggTier, int]` | โอกาสจากเวลานี้ |
| `next_bracket(duration_sec: int)` | `TierOdds \| None` | ทำตาม class แม่ |

### `HatchService`

- **ไฟล์:** `app/services/hatch_service.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `HatchService(store)`
- **หน้าที่:** ฟักไข่: สุ่มระดับไข่ (ถ้าไม่ได้ส่งมา) → สุ่มสัตว์ → ตัวใหม่หรือ level up → mark_hatched → save

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง |
| `factory` | `EggFactory` | สร้างใน `__init__` = `EggFactory()` | สร้างไข่ |
| `odds_table` | `TierOddsTable` | สร้างใน `__init__` = `TierOddsTable()` | ตารางโอกาสไข่ตามเวลา |
| `gacha` | `GachaMachine` | สร้างใน `__init__` = `GachaMachine()` | ตัวสุ่ม |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` | กติกา level/ขนาด |

| method | return | ทำอะไร |
|---|---|---|
| `roll_tier(duration_sec: int)` | `EggTier` | gacha.pick_tier(odds_table.odds_for(duration_sec)) · ต่ำกว่า 15 นาที → InvalidStateError |
| `hatch(session_id: int, tier: EggTier \| None = None)` | `HatchResult` | tier = None → roll_tier จากเวลาของ session · ห้องกลุ่มส่ง tier มา · ไม่ READY → InvalidStateError |
| `_give_pet(player_id: int, species: Species)` *private* | `tuple[OwnedPet, bool]` | มีแล้ว level_up / ยังไม่มีสร้างใหม่ · คืน (pet, is_new) |

## Frontend

**Import ที่ต้องใช้ (รวมทุกไฟล์ frontend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from typing import Any, Callable, ClassVar, TYPE_CHECKING
import asyncio

import flet as ft

from app.domain.enums import EggTier
from app.dto import HatchResult, PetDTO, TierOdds
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.base_widget import BaseWidget
from ui.core.format import Format
from ui.core.widgets import PixelButton

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

## Method ที่ต้องเขียนในไฟล์ของคนอื่น

ตัวแปรของ class เหล่านี้ P1 สร้างไว้แล้ว ให้เพิ่มเฉพาะ method ข้างล่าง

### `OwnedPet`

- **ไฟล์:** `app/domain/owned_pet.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **หน้าที่:** สัตว์ที่ผู้เล่นมี หนึ่งคนมีแต่ละชนิดได้ตัวเดียว ได้ซ้ำ = level up · P1 สร้างตัวแปร + to_dict/from_dict · P3 เขียน method ที่เหลือ

| method | return | ทำอะไร |
|---|---|---|
| `level_up(policy: PetLevelPolicy)` | `None` | times_hatched +1 และ level = policy.next_level(level) |
| `scale(policy: PetLevelPolicy)` | `float` | policy.scale_for(level) |
| `to_dto(species: Species, policy: PetLevelPolicy)` | `PetDTO` | แปลงเป็น PetDTO |

## เช็กลิสต์ก่อนส่ง PR

- [ ] TierOddsTable.odds_for(14*60) == {} และ odds_for(95*60) ได้ 15/45/40
- [ ] ทุก bracket และทุก rarity_weights รวมกัน = 100
- [ ] GachaMachine(seed=1) สุ่มซ้ำได้ผลเดิม
- [ ] pick_species เมื่อ pool ไม่มี rarity นั้น ต้องลดลงขั้นล่าง
- [ ] hatch ตัวซ้ำ → is_new False และ level +1
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
