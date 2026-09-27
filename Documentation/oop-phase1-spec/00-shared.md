# 00 · ของกลาง Phase 1 (ทุกคนอ่านก่อน)

CPE Egg Hatch · Phase 1 = 4 หน้า Landing → Lobby → Focus → Hatch/Result · ไม่มี login · CPEGO เป็น bubble · ข้อมูลอยู่ใน memory

## ใครทำอะไร

| คน | งาน | ไฟล์ |
|---|---|---|
| P1 | Landing + How to + Theme | [P1-landing-how-to-theme.md](P1-landing-how-to-theme.md) |
| P2 | Core data (in-memory) | [P2-core-data-in-memory.md](P2-core-data-in-memory.md) |
| P3 | Frontend core | [P3-frontend-core.md](P3-frontend-core.md) |
| P4 | Lobby + Sanctuary | [P4-lobby-sanctuary.md](P4-lobby-sanctuary.md) |
| P5 | Egg domain + Setup popup | [P5-egg-domain-setup-popup.md](P5-egg-domain-setup-popup.md) |
| P6 | Focus session | [P6-focus-session.md](P6-focus-session.md) |
| P7 | CPEGO bubble + Choose egg | [P7-cpego-bubble-choose-egg.md](P7-cpego-bubble-choose-egg.md) |
| P8 | Hatch logic | [P8-hatch-logic.md](P8-hatch-logic.md) |
| P9 | Hatch/Result page | [P9-hatch-result-page.md](P9-hatch-result-page.md) |

## กติกาที่ทุกคนต้องทำเหมือนกัน

| อะไร | แบบ | ตัวอย่าง |
|---|---|---|
| class | PascalCase | `FocusSessionService`, `SeniorEgg` |
| ตัวแปร, method, ไฟล์ | snake_case | `duration_sec`, `get_running()` |
| ค่าคงที่ | UPPER_SNAKE | `SCALE_STEP` |
| ใช้เฉพาะใน class (private) | ขึ้นต้น `_` | `_sent_minutes` |
| boolean | `is_` / `has_` / `can_` | `is_success()`, `can_hatch()` |
| เวลา ณ จุดหนึ่ง | ลงท้าย `_at` · `datetime` | `started_at` |
| ระยะเวลา | ลงท้าย `_sec` · `int` วินาที | `duration_sec` |
| รหัส | ลงท้าย `_id` / `_code` | `session_id`, `species_code` |

### ตัวแปรใน class มี 4 แบบ (คอลัมน์ "สร้างยังไง" ในตาราง)

| แบบ | เขียนในตารางว่า | ความหมาย |
|---|---|---|
| 1. ค่าคงที่ของ class | ค่าคงที่ของ class = ... | ประกาศใน class ใช้ร่วมกันทุก object เช่น `SCALE_STEP` |
| 2. ต้องส่งตอนสร้าง | ต้องส่งตอนสร้าง | เป็น parameter ของ `__init__` ที่ไม่มีค่าเริ่มต้น |
| 3. ส่งหรือไม่ก็ได้ | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = ... | parameter ของ `__init__` ที่มีค่าเริ่มต้น |
| 4. สถานะภายใน | สร้างใน `__init__` = ... | ไม่รับจากข้างนอก ตั้งค่าเริ่มต้นใน `__init__` แล้วเปลี่ยนผ่าน method เท่านั้น |

แถว **สร้าง** ของแต่ละ class บอกลำดับ parameter ของ `__init__` เช่น `StopwatchTimer(clock, started_at, on_tick, interval_sec=1.0)`

### ข้อตกลงการเขียน

- **service** รับ `GameStore` (และ `Clock`, `Settings` ถ้าต้องใช้) แล้วคืน DTO เท่านั้น ห้ามคืน `StudySession` / `OwnedPet` ออกไปให้หน้าจอ
- **หน้าจอ** เรียก backend ผ่าน `ctx.<service>` เช่น `ctx.focus.stop(...)` · โฟลเดอร์ `ui/` ห้าม import `app.data`
- **หน้าจอ** ต้องจับ `AppError` แล้วเรียก `show_error(error)` ทุกครั้งที่เรียก service
- สร้าง DTO ด้วย keyword เสมอ เช่น `StopResult(session_id=..., status=...)`
- เทียบ enum ด้วย `is` เช่น `status is SessionStatus.FAILED` ห้ามเทียบกับ string
- ผิดพลาดให้ raise ลูกของ `AppError` (`ValidationError`, `NotFoundError`, `InvalidStateError`)
- เวลาใช้ `Clock` เท่านั้น (รองรับโหมดเร่งเวลาตอนเดโม) · ตัวเลขตั้งค่าอยู่ใน `Settings`
- ใส่ type hint ทุกตัวแปรและทุก method · ไม่เขียนบรรทัด comment
- ห้ามเปลี่ยนชื่อ class, ตัวแปร, method หรือ parameter ในเอกสารนี้โดยไม่บอกกลุ่ม

## Enum, Error, DTO ที่ทุกคนใช้ (P2 ดูแล)

### `EggTier`

*Enum* · สืบทอดจาก `Enum` · `app/domain/enums.py`

ระดับไข่ 3 ระดับ

**สร้าง:** `EggTier.FRESHMAN`

| ค่า | ความหมาย |
|---|---|
| `FRESHMAN` | ไข่รุ่นเรา 15 นาที |
| `SENIOR` | ไข่รุ่นพี่ 30 นาที |
| `PROFESSOR` | ไข่อาจารย์ 60 นาที |

### `Rarity`

*Enum* · สืบทอดจาก `Enum` · `app/domain/enums.py`

ความหายากของสัตว์

**สร้าง:** `Rarity.COMMON`

| ค่า | ความหมาย |
|---|---|
| `COMMON` | ธรรมดา |
| `RARE` | หายาก |
| `EPIC` | หายากมาก |
| `LEGENDARY` | ตำนาน |

### `SessionStatus`

*Enum* · สืบทอดจาก `Enum` · `app/domain/enums.py`

สถานะของการอ่านหนึ่งรอบ

**สร้าง:** `SessionStatus.RUNNING`

| ค่า | ความหมาย |
|---|---|
| `RUNNING` | กำลังอ่าน |
| `READY_TO_HATCH` | หยุดหลัง 15 นาที รอเลือกไข่ |
| `HATCHED` | ฟักแล้ว |
| `FAILED` | หยุดก่อน 15 นาที |

### `AppError`

*Exception* · สืบทอดจาก `Exception` · `app/errors.py`

แม่ของ error ทุกตัว หน้าจอจับ AppError แล้วโชว์ message

**สร้าง:** `AppError(message, field=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `message` | `str` | ต้องส่งตอนสร้าง | ข้อความที่โชว์ผู้ใช้ |
| `field` | `str \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ชื่อช่องที่ผิด เช่น "subject" |

### `ValidationError`

*class* · สืบทอดจาก `AppError` · `app/errors.py`

ข้อมูลที่กรอกไม่ถูก เช่น ไม่ใส่ชื่อวิชา

**สร้าง:** `ValidationError("ข้อความ", field="email")`

### `NotFoundError`

*class* · สืบทอดจาก `AppError` · `app/errors.py`

หาข้อมูลไม่เจอ เช่น session_id ไม่มี

**สร้าง:** `NotFoundError("ข้อความ", field="email")`

### `InvalidStateError`

*class* · สืบทอดจาก `AppError` · `app/errors.py`

ทำผิดลำดับ เช่น hatch ทั้งที่ยังไม่ READY_TO_HATCH

**สร้าง:** `InvalidStateError("ข้อความ", field="email")`

### `SpeciesDTO`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ข้อมูลสัตว์หนึ่งชนิดที่ส่งให้หน้าจอ

**สร้าง:** `SpeciesDTO(code=..., name=..., tier=..., rarity=..., sprite_path=..., description=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `code` | `str` | ต้องส่งตอนสร้าง | รหัสไม่ซ้ำ เช่น "debug_duck" |
| `name` | `str` | ต้องส่งตอนสร้าง | ชื่อที่โชว์ |
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ออกจากไข่ระดับไหน |
| `rarity` | `Rarity` | ต้องส่งตอนสร้าง | ความหายาก |
| `sprite_path` | `str` | ต้องส่งตอนสร้าง | path รูปใน assets |
| `description` | `str` | ต้องส่งตอนสร้าง | คำอธิบายสั้น |

### `TierInfo`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ข้อมูลไข่หนึ่งระดับ (Egg Rate, Choose an egg)

**สร้าง:** `TierInfo(tier=..., name_th=..., required_minutes=..., rarity_weights=..., image_path=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ระดับ |
| `name_th` | `str` | ต้องส่งตอนสร้าง | ชื่อไทย |
| `required_minutes` | `int` | ต้องส่งตอนสร้าง | เวลาขั้นต่ำ |
| `rarity_weights` | `dict[Rarity, int]` | ต้องส่งตอนสร้าง | โอกาสแต่ละ rarity รวม 100 |
| `image_path` | `str` | ต้องส่งตอนสร้าง | รูปไข่ |

### `SessionDTO`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

การอ่านหนึ่งรอบ ตอนเริ่ม

**สร้าง:** `SessionDTO(id=..., subject=..., started_at=..., status=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | session_id |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `status` | `SessionStatus` | ต้องส่งตอนสร้าง | สถานะ |

### `StopResult`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ผลหลังกด STOP

**สร้าง:** `StopResult(session_id=..., status=..., duration_sec=..., unlocked_tiers=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | session |
| `status` | `SessionStatus` | ต้องส่งตอนสร้าง | FAILED หรือ READY_TO_HATCH |
| `duration_sec` | `int` | ต้องส่งตอนสร้าง | เวลาที่อ่าน (วินาที) |
| `unlocked_tiers` | `list[EggTier]` | ต้องส่งตอนสร้าง | ไข่ที่เลือกได้ ว่างถ้า FAILED |

### `PetDTO`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

สัตว์หนึ่งตัวในห้องภาค

**สร้าง:** `PetDTO(species=..., level=..., scale=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `species` | `SpeciesDTO` | ต้องส่งตอนสร้าง | ชนิด |
| `level` | `int` | ต้องส่งตอนสร้าง | level เริ่ม 1 |
| `scale` | `float` | ต้องส่งตอนสร้าง | ขนาด 1.0 ถึง 2.0 |

### `HatchResult`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ผลการฟักไข่

**สร้าง:** `HatchResult(session_id=..., tier=..., pet=..., is_new=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | session |
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ไข่ที่เลือก |
| `pet` | `PetDTO` | ต้องส่งตอนสร้าง | สัตว์ที่ได้ (level หลังอัปเดต) |
| `is_new` | `bool` | ต้องส่งตอนสร้าง | True = ตัวใหม่, False = ตัวซ้ำ level up |

### `SessionReport`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ข้อมูลสรุปผลในหน้า Result

**สร้าง:** `SessionReport(session_id=..., subject=..., status=..., is_success=..., duration_sec=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | session |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `status` | `SessionStatus` | ต้องส่งตอนสร้าง | HATCHED หรือ FAILED |
| `is_success` | `bool` | ต้องส่งตอนสร้าง | True ถ้า HATCHED |
| `duration_sec` | `int` | ต้องส่งตอนสร้าง | เวลาที่อ่าน |
| `remaining_sec` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `0` | ถ้าไม่สำเร็จ ต้องอ่านอีกกี่วินาทีถึงจะได้ไข่ |
| `tier` | `EggTier \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ไข่ที่เลือก |
| `pet` | `PetDTO \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | สัตว์ที่ได้ |
| `is_new` | `bool \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ได้ตัวใหม่ไหม |
