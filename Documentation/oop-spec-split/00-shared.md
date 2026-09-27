# 00 · ของกลาง (ทุกคนอ่านก่อน) · แบบแยกฝั่ง

CPE Egg Hatch · Python OOP · Frontend = Flet · Backend = class Python ในโปรแกรมเดียวกัน · เก็บข้อมูลเป็น `save.json` · รันบนเครื่องเดียว

## Feature ที่ทำ

| # | Feature | ทำอะไร | Backend | Frontend |
|---|---|---|---|---|
| 1 | CPE Tier | ไข่ 3 ระดับ ยิ่งอ่านนานยิ่งมีสิทธิ์ลุ้นไข่สูง แต่ไม่การันตี | B2 | F2 (ตารางโอกาส), F4 (หน้าฟักไข่) |
| 2 | Study Timer | จับเวลาอ่านเดี่ยว นับขึ้น CPEGO แจ้งเมื่อเข้าช่วงโอกาสใหม่ | B3 | F2 |
| 3 | Shared Fate | อ่านกลุ่ม 2–6 คนบนเครื่องเดียว ชะตาเดียวกัน | B3 | F3 |
| 4 | Department Sanctuary | สัตว์ที่ได้เดินไปมาในห้องภาค ตัวซ้ำ = level ขึ้น ตัวใหญ่ขึ้น | B3 | F4 |
| 5 | CPE Dex | สมุดสะสมสัตว์ทุกชนิด ปลดล็อกแล้ว/ยัง + วิชาที่อ่าน | B3 | F4 |
| 6 | Analytics | สรุปผลรายรอบ + ประวัติ + สถิติรวม | B3 | F3 |
| – | Core | ข้อมูล, ที่เก็บ, ผู้เล่น · โครงหน้าจอ, หน้า Landing | B1 | F1 |

ไม่ทำ: Egg Crack, Tab Detection, BGM, login/รหัสผ่าน (ใช้แค่ชื่อเล่น)

## ใครทำอะไร

| คน | ฝั่ง | งาน | Class | ไฟล์ |
|---|---|---|---|---|
| B1 | Backend | Core Data | `Settings`, `Clock`, `Player`, `Species`, `StudySession`, `OwnedPet`, `GroupRoom`, `BaseRepository`, `PlayerRepository`, `SpeciesRepository`, `SessionRepository`, `PetRepository`, `RoomRepository`, `SaveFile`, `SpeciesLoader`, `GameStore`, `PlayerService` | [B1-core-data.md](B1-core-data.md) |
| B2 | Backend | Egg & Hatch Logic | `Egg`, `FreshmanEgg`, `SeniorEgg`, `ProfessorEgg`, `EggFactory`, `TierOddsTable`, `GachaMachine`, `PetLevelPolicy`, `TierService`, `HatchService` | [B2-egg-hatch-logic.md](B2-egg-hatch-logic.md) |
| B3 | Backend | Session, Room & Stats | `FocusSessionService`, `RoomService`, `SanctuaryService`, `DexService`, `StatsCalculator`, `AnalyticsService` | [B3-session-room-stats.md](B3-session-room-stats.md) |
| F1 | Frontend | UI Core + Landing | `BaseWidget`, `BaseView`, `Navigator`, `AppContext`, `Theme`, `SoundManager`, `PixelButton`, `Popup`, `ConfirmDialog`, `StatTile`, `Format`, `HowToSlide`, `HowToPopup`, `PlayerPicker`, `LandingView` | [F1-ui-core-landing.md](F1-ui-core-landing.md) |
| F2 | Frontend | Focus UI | `EggOddsPanel`, `StopwatchTimer`, `CpegoMessage`, `CpegoBot`, `CpegoBubble`, `EggView`, `SetupPopup`, `FocusView` | [F2-focus-ui.md](F2-focus-ui.md) |
| F3 | Frontend | Room + Result UI | `MemberPicker`, `RoomSetupView`, `MemberList`, `RoomFocusView`, `ResultCard`, `ResultView`, `BarChart`, `HistoryView` | [F3-room-result-ui.md](F3-room-result-ui.md) |
| F4 | Frontend | Lobby, Dex + Hatch UI | `HatchAnimation`, `HatchView`, `PetSprite`, `SanctuaryScene`, `LobbyView`, `DexCard`, `DexDetailPanel`, `DexView` | [F4-lobby-dex-hatch-ui.md](F4-lobby-dex-hatch-ui.md) |

## ทำงานแบบแยกฝั่งยังไงไม่ให้รอกัน

- **สัญญากลางคือ DTO กับชื่อ method ของ service** (ตารางในไฟล์ B1–B3) ฝั่ง frontend เขียนหน้าจอตามสัญญานี้ได้เลยโดยไม่ต้องรอ backend
- **ช่วงแรก frontend ใช้ service ปลอม:** เขียน class ที่มีชื่อ method เดียวกันแต่คืน DTO ตายตัว แล้วใส่แทนใน `AppContext` ชั่วคราว พอ backend เสร็จเปลี่ยนกลับบรรทัดเดียว
- **backend เทสต์ด้วย pytest อย่างเดียว** ไม่ต้องเปิดหน้าจอ
- **ถ้าจะเปลี่ยน field ของ DTO หรือ parameter ของ method** ต้องบอกทั้งคนทำ backend และ frontend ที่เกี่ยวข้องก่อน (ดูคอลัมน์ "ใครใช้ของเรา")
- **B1 กับ F1 ต้องเสร็จก่อนคนอื่น** B1: model + `GameStore` + DTO · F1: `AppContext` + `Navigator` + `BaseView` + widget กลาง

## กติกาไข่

**ขั้นที่ 1 สุ่มระดับไข่ตามเวลาที่อ่าน** (`TierOddsTable`) ยิ่งอ่านนาน โอกาสได้ไข่สูงยิ่งมาก แต่ไม่ได้เสมอไป

| เวลาที่อ่าน | ไข่รุ่นเรา | ไข่รุ่นพี่ | ไข่อาจารย์ |
|---|---|---|---|
| ต่ำกว่า 15 นาที | ไม่ได้ไข่ | | |
| 15–29 นาที | 85% | 13% | 2% |
| 30–59 นาที | 55% | 35% | 10% |
| 60–89 นาที | 30% | 45% | 25% |
| 90 นาทีขึ้นไป | 15% | 45% | 40% |

**ขั้นที่ 2 สุ่ม rarity ตามไข่ที่ได้** (`Egg.rarity_weights`) แล้วสุ่มสัตว์ 1 ตัวจาก rarity นั้น

| ไข่ | Common | Rare | Epic | Legendary |
|---|---|---|---|---|
| ไข่รุ่นเรา | 70% | 25% | 5% | 0% |
| ไข่รุ่นพี่ | 40% | 40% | 17% | 3% |
| ไข่อาจารย์ | 10% | 40% | 35% | 15% |

- ได้ตัวใหม่ → เพิ่มเข้าห้องภาค level 1 · ได้ตัวซ้ำ → level +1 ขนาด +15% (สูงสุด 2 เท่า)
- **Shared Fate:** หยุดก่อน 15 นาที ทุกคนไม่ได้ไข่ · ถึงแล้วสุ่มระดับไข่ครั้งเดียว ทุกคนได้ระดับเดียวกัน แต่ละคนสุ่มสัตว์ของตัวเอง

## Flow

1. **Landing** เลือกหรือสร้างผู้เล่น → **Lobby**
2. **Lobby** → START FOCUS → popup ใส่วิชา → **Focus** → STOP → YES
3. ไม่ถึง 15 นาที → **Result** (ไม่สำเร็จ) · ถึง → **Hatch** → **Result**
4. **Lobby** → GROUP STUDY → **Room Setup** เลือกสมาชิก → **Room** → STOP → **Hatch** (ทุกคน) → **Result** (ทุกคน)
5. **Result** → RETURN TO LOBBY · **Lobby** → DEX / HISTORY

## เส้นทางหน้าจอ

| route | หน้า | class | เจ้าของ | params |
|---|---|---|---|---|
| `/` | Landing (เลือก/สร้างผู้เล่น) | `LandingView` | F1 | – |
| `/lobby` | ห้องภาค | `LobbyView` | F4 | – |
| `/focus` | อ่านเดี่ยว | `FocusView` | F2 | `session_id` |
| `/room/setup` | ตั้งห้องกลุ่ม | `RoomSetupView` | F3 | – |
| `/room` | อ่านกลุ่ม | `RoomFocusView` | F3 | `room_id` |
| `/hatch` | ฟักไข่ | `HatchView` | F4 | `session_id` หรือ `room_id` |
| `/result` | สรุปผล | `ResultView` | F3 | `session_id` หรือ `room_id` |
| `/dex` | CPE Dex | `DexView` | F4 | – |
| `/history` | ประวัติ + สถิติ | `HistoryView` | F3 | – |

## ไฟล์ save.json

`GameStore.save()` เขียน 4 ส่วน: `players`, `sessions`, `pets`, `rooms` (แต่ละส่วนเป็น list ของ dict จาก `to_dict()`) · สัตว์ทุกชนิดอ่านจาก `seed/species.json` ไม่บันทึกลง save · datetime เก็บเป็น ISO string · Enum เก็บเป็น `.value`

## กติกาการตั้งชื่อ

| อะไร | แบบ | ตัวอย่าง |
|---|---|---|
| class | PascalCase | `FocusSessionService` |
| ตัวแปร, method, ไฟล์ | snake_case | `duration_sec`, `get_running()`, `focus_service.py` |
| ค่าคงที่ | UPPER_SNAKE | `SCALE_STEP`, `BRACKETS` |
| ใช้เฉพาะใน class | ขึ้นต้น `_` | `_announced`, `_give_pet()` |
| boolean | `is_` / `has_` / `can_` | `is_success()`, `can_hatch()` |
| เวลา ณ จุดหนึ่ง | ลงท้าย `_at` · `datetime` UTC | `started_at` |
| ระยะเวลา | ลงท้าย `_sec` · `int` วินาที | `duration_sec` |
| รหัส | ลงท้าย `_id` / `_code` | `player_id`, `species_code` |
| list / dict | พหูพจน์ | `member_ids`, `tier_odds` |
| widget ที่เก็บไว้ | ลงท้ายด้วยชนิด | `subject_field`, `time_text` |

## ตัวแปรใน class มี 4 แบบ (คอลัมน์ "สร้างยังไง")

| แบบ | เขียนในตารางว่า | ความหมาย |
|---|---|---|
| 1. ค่าคงที่ของ class | ค่าคงที่ของ class = ... | ประกาศใน class ใช้ร่วมกันทุก object |
| 2. ต้องส่งตอนสร้าง | ต้องส่งตอนสร้าง | parameter ของ `__init__` ไม่มีค่าเริ่มต้น |
| 3. ส่งหรือไม่ก็ได้ | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = ... | parameter ของ `__init__` มีค่าเริ่มต้น (ถ้าเป็น list/dict/set ให้รับ `None` แล้วสร้างใหม่ข้างใน) |
| 4. สถานะภายใน | สร้างใน `__init__` = ... | ไม่รับจากข้างนอก ตั้งค่าใน `__init__` แล้วเปลี่ยนผ่าน method เท่านั้น |

บรรทัด **สร้าง** ของแต่ละ class คือลำดับ parameter ของ `__init__` ห้ามสลับ

## Clean code

- **ทุกไฟล์บรรทัดแรก** `from __future__ import annotations` · ใส่ type hint ทุกตัวแปรและทุก method · ไม่เขียนบรรทัด comment ตั้งชื่อให้อ่านรู้เรื่องแทน
- **หนึ่ง method ทำเรื่องเดียว** ยาวไม่เกินประมาณ 20 บรรทัด ยาวกว่านั้นแตกเป็น method `_ชื่อ` ใน class เดียวกัน
- **return เร็ว** เช็กเงื่อนไขผิดแล้ว `raise` หรือ `return` ก่อน ไม่ซ้อน if หลายชั้น
- **ไม่มีเลขลอย ๆ** ตัวเลขตั้งค่าอยู่ใน `Settings` หรือค่าคงที่ของ class เช่น `15 * 60` ต้องเป็น `settings.min_success_minutes * 60`
- **เวลา** ขอจาก `Clock` เท่านั้น ห้ามเรียก `datetime.now()` เอง (ไม่งั้นโหมดเร่งเวลาจะพัง)
- **service** รับ `GameStore` แล้วคืน DTO เท่านั้น ห้ามคืน model (`StudySession`, `OwnedPet`, `GroupRoom`, `Player`) ให้หน้าจอ · service ที่แก้ข้อมูลเรียก `self.store.save()` ท้าย method
- **หน้าจอ** เรียก backend ผ่าน `ctx.<service>` เท่านั้น · โฟลเดอร์ `ui/` ห้าม import `app.data` และห้ามแก้ model ตรง ๆ · ทุกครั้งที่เรียก service ให้ `try` / `except AppError as error: self.show_error(error)`
- **โฟลเดอร์ `app/` ห้าม `import flet`**
- **สร้าง DTO ด้วย keyword** เช่น `StopResult(session_id=..., status=...)`
- **เทียบ enum ด้วย `is`** เช่น `status is SessionStatus.FAILED` ห้ามเทียบกับ string
- **error** raise ลูกของ `AppError` เท่านั้น ใส่ `field=` ถ้าเกี่ยวกับช่องกรอก
- **loop ที่วนทุกวินาที** ใช้ `page.run_task` + `await asyncio.sleep(...)` ห้าม `time.sleep` · หยุด loop ใน `on_leave()` เสมอ
- **ถ้า import กันไปมาแล้ว error circular import** ย้ายตัวที่ใช้แค่เป็น type hint ไปไว้ใต้ `if TYPE_CHECKING:`
- **ห้ามเปลี่ยนชื่อ class, ตัวแปร, method หรือ parameter ในเอกสารนี้** โดยไม่บอกกลุ่ม
- **ติดตั้ง** `pip install flet flet-audio pytest` · เทสต์ backend ด้วย `pytest` ใน `tests/`

## Enum, Error, DTO ที่ทุกคนใช้ (B1 ดูแล)

**ต้อง import:**

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
```

### `EggTier`

- **ไฟล์:** `app/domain/enums.py`
- **ชนิด:** Enum
- **inherit:** `Enum`
- **สร้าง:** `EggTier.FRESHMAN`
- **หน้าที่:** ระดับไข่ 3 ระดับ

| ค่า | value | ความหมาย |
|---|---|---|
| `FRESHMAN` | `"freshman"` | ไข่รุ่นเรา |
| `SENIOR` | `"senior"` | ไข่รุ่นพี่ |
| `PROFESSOR` | `"professor"` | ไข่อาจารย์ |

### `Rarity`

- **ไฟล์:** `app/domain/enums.py`
- **ชนิด:** Enum
- **inherit:** `Enum`
- **สร้าง:** `Rarity.COMMON`
- **หน้าที่:** ความหายากของสัตว์

| ค่า | value | ความหมาย |
|---|---|---|
| `COMMON` | `"common"` | ธรรมดา |
| `RARE` | `"rare"` | หายาก |
| `EPIC` | `"epic"` | หายากมาก |
| `LEGENDARY` | `"legendary"` | ตำนาน |

### `SessionStatus`

- **ไฟล์:** `app/domain/enums.py`
- **ชนิด:** Enum
- **inherit:** `Enum`
- **สร้าง:** `SessionStatus.RUNNING`
- **หน้าที่:** สถานะการอ่านหนึ่งรอบของผู้เล่นหนึ่งคน

| ค่า | value | ความหมาย |
|---|---|---|
| `RUNNING` | `"running"` | กำลังอ่าน |
| `READY_TO_HATCH` | `"ready_to_hatch"` | หยุดหลัง 15 นาที รอฟัก |
| `HATCHED` | `"hatched"` | ฟักแล้ว |
| `FAILED` | `"failed"` | หยุดก่อน 15 นาที |

### `RoomStatus`

- **ไฟล์:** `app/domain/enums.py`
- **ชนิด:** Enum
- **inherit:** `Enum`
- **สร้าง:** `RoomStatus.RUNNING`
- **หน้าที่:** สถานะห้องอ่านกลุ่ม

| ค่า | value | ความหมาย |
|---|---|---|
| `RUNNING` | `"running"` | กำลังอ่าน |
| `READY_TO_HATCH` | `"ready_to_hatch"` | หยุดหลัง 15 นาที รอฟัก |
| `HATCHED` | `"hatched"` | ฟักแล้วทุกคน |
| `FAILED` | `"failed"` | หยุดก่อน 15 นาที ทุกคนไม่ได้ไข่ |

### `AppError`

- **ไฟล์:** `app/errors.py`
- **ชนิด:** Exception
- **inherit:** `Exception`
- **สร้าง:** `AppError(message, field=None)`
- **หน้าที่:** แม่ของ error ทุกตัว หน้าจอจับ AppError แล้วโชว์ message

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `message` | `str` | ต้องส่งตอนสร้าง | ข้อความที่โชว์ผู้ใช้ |
| `field` | `str \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ชื่อช่องที่ผิด เช่น "subject" |

### `ValidationError`

- **ไฟล์:** `app/errors.py`
- **ชนิด:** class
- **inherit:** `AppError`
- **สร้าง:** `ValidationError("ข้อความ", field="email")`
- **หน้าที่:** ข้อมูลที่กรอกไม่ถูก เช่น ไม่ใส่ชื่อวิชา ชื่อเล่นซ้ำ

### `NotFoundError`

- **ไฟล์:** `app/errors.py`
- **ชนิด:** class
- **inherit:** `AppError`
- **สร้าง:** `NotFoundError("ข้อความ", field="email")`
- **หน้าที่:** หาข้อมูลไม่เจอ เช่น session_id ไม่มี

### `InvalidStateError`

- **ไฟล์:** `app/errors.py`
- **ชนิด:** class
- **inherit:** `AppError`
- **สร้าง:** `InvalidStateError("ข้อความ", field="email")`
- **หน้าที่:** ทำผิดลำดับ เช่น ฟักไข่ทั้งที่ยังไม่ READY_TO_HATCH

### `PlayerDTO`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `PlayerDTO(id=..., nickname=...)`
- **หน้าที่:** ผู้เล่นหนึ่งคน

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | player_id |
| `nickname` | `str` | ต้องส่งตอนสร้าง | ชื่อเล่น |

### `SpeciesDTO`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `SpeciesDTO(code=..., name=..., tier=..., rarity=..., sprite_path=..., description=...)`
- **หน้าที่:** สัตว์หนึ่งชนิด

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `code` | `str` | ต้องส่งตอนสร้าง | รหัสไม่ซ้ำ เช่น "debug_duck" |
| `name` | `str` | ต้องส่งตอนสร้าง | ชื่อที่โชว์ |
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ออกจากไข่ระดับไหน |
| `rarity` | `Rarity` | ต้องส่งตอนสร้าง | ความหายาก |
| `sprite_path` | `str` | ต้องส่งตอนสร้าง | path รูป |
| `description` | `str` | ต้องส่งตอนสร้าง | คำอธิบาย |

### `TierInfo`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `TierInfo(tier=..., name_th=..., rarity_weights=..., image_path=...)`
- **หน้าที่:** ข้อมูลไข่หนึ่งระดับ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ระดับ |
| `name_th` | `str` | ต้องส่งตอนสร้าง | ชื่อไทย |
| `rarity_weights` | `dict[Rarity, int]` | ต้องส่งตอนสร้าง | โอกาสแต่ละ rarity ในไข่นี้ รวม 100 |
| `image_path` | `str` | ต้องส่งตอนสร้าง | รูปไข่ |

### `TierOdds`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `TierOdds(min_minutes=..., max_minutes=..., weights=...)`
- **หน้าที่:** โอกาสได้ไข่แต่ละระดับในช่วงเวลาหนึ่ง

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `min_minutes` | `int` | ต้องส่งตอนสร้าง | เริ่มต้นช่วง (รวม) |
| `max_minutes` | `int \| None` | ต้องส่งตอนสร้าง | จบช่วง (ไม่รวม) None = ไม่มีเพดาน |
| `weights` | `dict[EggTier, int]` | ต้องส่งตอนสร้าง | โอกาสแต่ละระดับ รวม 100 |

### `SessionDTO`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `SessionDTO(id=..., player_id=..., subject=..., started_at=..., status=...)`
- **หน้าที่:** การอ่านหนึ่งรอบ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | session_id |
| `player_id` | `int` | ต้องส่งตอนสร้าง | ผู้เล่น |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `status` | `SessionStatus` | ต้องส่งตอนสร้าง | สถานะ |
| `room_id` | `int \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ห้องกลุ่ม ถ้าอ่านเดี่ยว = None |

### `StopResult`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `StopResult(session_id=..., status=..., duration_sec=..., tier_odds=...)`
- **หน้าที่:** ผลหลังกด STOP (อ่านเดี่ยว)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | - |
| `status` | `SessionStatus` | ต้องส่งตอนสร้าง | FAILED หรือ READY_TO_HATCH |
| `duration_sec` | `int` | ต้องส่งตอนสร้าง | เวลาที่อ่าน |
| `tier_odds` | `dict[EggTier, int]` | ต้องส่งตอนสร้าง | โอกาสได้ไข่แต่ละระดับจากเวลานี้ ว่างถ้า FAILED |

### `PetDTO`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `PetDTO(species=..., level=..., scale=...)`
- **หน้าที่:** สัตว์หนึ่งตัวที่ผู้เล่นมี

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `species` | `SpeciesDTO` | ต้องส่งตอนสร้าง | ชนิด |
| `level` | `int` | ต้องส่งตอนสร้าง | level เริ่ม 1 |
| `scale` | `float` | ต้องส่งตอนสร้าง | ขนาด 1.0 ถึง 2.0 |

### `HatchResult`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `HatchResult(session_id=..., player_id=..., tier=..., pet=..., is_new=...)`
- **หน้าที่:** ผลการฟักไข่ของผู้เล่นหนึ่งคน

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | - |
| `player_id` | `int` | ต้องส่งตอนสร้าง | - |
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ระดับไข่ที่สุ่มได้ |
| `pet` | `PetDTO` | ต้องส่งตอนสร้าง | สัตว์ที่ได้ (level หลังอัปเดต) |
| `is_new` | `bool` | ต้องส่งตอนสร้าง | True = ตัวใหม่ |

### `RoomDTO`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `RoomDTO(id=..., subject=..., members=..., started_at=..., status=..., session_ids=...)`
- **หน้าที่:** ห้องอ่านกลุ่ม

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | room_id |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `members` | `list[PlayerDTO]` | ต้องส่งตอนสร้าง | สมาชิก 2–6 คน |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `status` | `RoomStatus` | ต้องส่งตอนสร้าง | สถานะ |
| `session_ids` | `list[int]` | ต้องส่งตอนสร้าง | session ของสมาชิกแต่ละคน เรียงตาม members |

### `RoomStopResult`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `RoomStopResult(room_id=..., status=..., duration_sec=..., tier_odds=...)`
- **หน้าที่:** ผลหลังกด STOP ห้องกลุ่ม

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `room_id` | `int` | ต้องส่งตอนสร้าง | - |
| `status` | `RoomStatus` | ต้องส่งตอนสร้าง | FAILED หรือ READY_TO_HATCH |
| `duration_sec` | `int` | ต้องส่งตอนสร้าง | เวลาที่อ่าน |
| `tier_odds` | `dict[EggTier, int]` | ต้องส่งตอนสร้าง | โอกาสได้ไข่ ว่างถ้า FAILED |

### `RoomHatchResult`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `RoomHatchResult(room_id=..., tier=..., results=...)`
- **หน้าที่:** ผลการฟักไข่ของทั้งห้อง

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `room_id` | `int` | ต้องส่งตอนสร้าง | - |
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ระดับไข่ที่ทุกคนได้เหมือนกัน |
| `results` | `list[HatchResult]` | ต้องส่งตอนสร้าง | ผลของสมาชิกแต่ละคน |

### `DexEntry`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `DexEntry(species=..., unlocked=...)`
- **หน้าที่:** หนึ่งช่องใน CPE Dex

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `species` | `SpeciesDTO` | ต้องส่งตอนสร้าง | ชนิด |
| `unlocked` | `bool` | ต้องส่งตอนสร้าง | เคยได้หรือยัง |
| `level` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `0` | level ปัจจุบัน 0 = ยังไม่เคยได้ |
| `times_hatched` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `0` | ฟักได้กี่ครั้ง |
| `first_hatched_at` | `datetime \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ได้ครั้งแรกเมื่อไหร่ |
| `subjects` | `list[str]` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `[]` | วิชาที่อ่านตอนได้ตัวนี้ ไม่ซ้ำ |

### `SessionReport`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `SessionReport(session_id=..., player_id=..., subject=..., status=..., is_success=..., duration_sec=..., started_at=..., ended_at=...)`
- **หน้าที่:** สรุปผลการอ่านหนึ่งรอบของผู้เล่นหนึ่งคน

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | - |
| `player_id` | `int` | ต้องส่งตอนสร้าง | - |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `status` | `SessionStatus` | ต้องส่งตอนสร้าง | HATCHED หรือ FAILED |
| `is_success` | `bool` | ต้องส่งตอนสร้าง | True ถ้า HATCHED |
| `duration_sec` | `int` | ต้องส่งตอนสร้าง | เวลาที่อ่าน |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `ended_at` | `datetime \| None` | ต้องส่งตอนสร้าง | - |
| `remaining_sec` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `0` | ไม่สำเร็จ: ต้องอ่านอีกกี่วินาทีถึงจะได้ไข่ |
| `tier` | `EggTier \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ไข่ที่ได้ |
| `pet` | `PetDTO \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | สัตว์ที่ได้ |
| `is_new` | `bool \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ได้ตัวใหม่ไหม |
| `room_id` | `int \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ห้องกลุ่ม |

### `HistoryStats`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `HistoryStats(total_sessions=..., success_count=..., fail_count=..., success_rate=..., total_study_sec=..., tier_counts=..., subject_study_sec=..., daily_study_sec=...)`
- **หน้าที่:** สถิติรวมของผู้เล่นหนึ่งคน

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `total_sessions` | `int` | ต้องส่งตอนสร้าง | จำนวนรอบ |
| `success_count` | `int` | ต้องส่งตอนสร้าง | รอบที่สำเร็จ |
| `fail_count` | `int` | ต้องส่งตอนสร้าง | รอบที่ไม่สำเร็จ |
| `success_rate` | `float` | ต้องส่งตอนสร้าง | 0.0 ถึง 1.0 |
| `total_study_sec` | `int` | ต้องส่งตอนสร้าง | เวลาอ่านรวม |
| `tier_counts` | `dict[EggTier, int]` | ต้องส่งตอนสร้าง | ได้ไข่แต่ละระดับกี่ครั้ง |
| `subject_study_sec` | `dict[str, int]` | ต้องส่งตอนสร้าง | เวลาอ่านแยกวิชา |
| `daily_study_sec` | `dict[str, int]` | ต้องส่งตอนสร้าง | เวลาอ่านรายวัน key = "2026-09-27" (7 วันล่าสุด) |

### `History`

- **ไฟล์:** `app/dto.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `History(reports=..., stats=...)`
- **หน้าที่:** ข้อมูลหน้า History

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `reports` | `list[SessionReport]` | ต้องส่งตอนสร้าง | ทุกรอบ ใหม่สุดก่อน |
| `stats` | `HistoryStats` | ต้องส่งตอนสร้าง | สถิติรวม |
