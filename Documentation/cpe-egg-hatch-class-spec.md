# CPE Egg Hatch Class Spec

นิยาม class ทุกตัวที่ทีม 9 คนต้องเขียน (93 class): หน้าที่, สืบทอดจากอะไร, อยู่ไฟล์ไหน, วิธีสร้าง object, ตัวแปรทุกตัว (ชนิด + สร้างยังไง) และ method ทุกตัว ชื่อทั้งหมดตรงกับโครงโปรเจกต์ `cpe_egg_hatch` เริ่มอ่านจากหัวข้อ "ของกลาง" ก่อน แล้วไปส่วนของตัวเอง

## สารบัญ

- [ของกลาง](#shared)
- [P1 · Auth](#p1)
- [P2 · Backend core + Data](#p2)
- [P3 · Frontend core + How to](#p3)
- [P4 · Department Sanctuary](#p4)
- [P5 · Set up + Egg domain](#p5)
- [P6 · Focus session + CPEGO](#p6)
- [P7 · Summary + Session Report](#p7)
- [P8 · Hatch / Gacha](#p8)
- [P9 · CPE Dex + History](#p9)

<a id="shared"></a>

## ของกลาง

ทุกคนต้องอ่าน · P2 เป็นคนดูแล · 20 class · 3 ไฟล์

### กติกาการตั้งชื่อ

| อะไร | แบบ | ตัวอย่าง |
| --- | --- | --- |
| class | PascalCase | `FocusSessionService`, `SeniorEgg` |
| ตัวแปร, method, ชื่อไฟล์ | snake\_case | `duration_sec`, `get_running()`, `focus_service.py` |
| ค่าคงที่ | UPPER\_SNAKE | `MIN_PASSWORD_LEN`, `SCALE_STEP` |
| ใช้เฉพาะใน class (private) | ขึ้นต้นด้วย `_` | `_sent_minutes`, `_registry` |
| boolean | `is_` / `has_` / `can_` | `is_success()`, `can_hatch()`, `is_new` |
| เวลา ณ จุดหนึ่ง | ลงท้าย `_at` · `datetime` UTC | `started_at`, `ended_at` |
| ระยะเวลา | ลงท้าย `_sec` · `int` วินาที | `duration_sec`, `elapsed_sec` |
| รหัส | ลงท้าย `_id` · `int` | `session_id`, `species_id` |
| list / dict | คำนามพหูพจน์ | `sprites`, `unlocked_tiers`, `rarity_weights` |
| widget ของ Flet ที่เก็บไว้ | ลงท้ายด้วยชนิด | `email_field`, `time_text`, `list_view` |

### ตัวแปรใน class มี 4 แบบ

คอลัมน์ "สร้างยังไง" ในแต่ละ class บอกว่าตัวแปรนั้นเป็นแบบไหน

```python
class StopwatchTimer:
    TICK_LIMIT: ClassVar[int] = 99

    def __init__(
        self,
        started_at: datetime,
        on_tick: Callable[[int], None],
        interval_sec: float = 1.0,
    ) -> None:
        self.started_at = started_at
        self.on_tick = on_tick
        self.interval_sec = interval_sec
        self.running: bool = False
```

| แบบ | ในตาราง | ตัวอย่าง |
| --- | --- | --- |
| 1. ค่าคงที่ของ class | ค่าคงที่ของ class | `TICK_LIMIT` ใช้ร่วมกันทุก object |
| 2. ต้องส่งตอนสร้าง | ต้องส่งตอนสร้าง | `started_at`, `on_tick` |
| 3. ส่งหรือไม่ก็ได้ | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = ... | `interval_sec` |
| 4. สถานะภายใน | สร้างใน \_\_init\_\_ = ... | `running` เริ่มเป็น `False` เปลี่ยนผ่าน method |

### รูปแบบที่ทุกคนต้องเขียนเหมือนกัน

**Service: เปิด database ด้วย UnitOfWork**

```python
def stop(self, session_id: int) -> StopResult:
    with UnitOfWork(self.database) as uow:
        session = uow.sessions.get_or_raise(session_id)
        status = session.stop(utcnow(), self.settings.min_success_minutes * 60)
        eggs = self.factory.unlocked_for(session.duration_sec)
        return StopResult(
            session_id=session.id,
            status=status,
            duration_sec=session.duration_sec,
            unlocked_tiers=[egg.tier for egg in eggs],
        )
```

**View: เรียก service ผ่าน ctx แล้วจับ AppError**

```python
def confirm_stop(self) -> None:
    try:
        result = self.ctx.focus.stop(self.session.id)
    except AppError as error:
        self.show_error(error)
        return
    if result.status is SessionStatus.FAILED:
        self.ctx.nav.go("/report", session_id=result.session_id)
    else:
        self.ctx.nav.go("/summary", session_id=result.session_id)
```

- สร้าง DTO ด้วย keyword เสมอ `StopResult(session_id=..., status=...)` ไม่ใส่ตามตำแหน่ง
- service คืน DTO เท่านั้น ห้ามคืน model (`User`, `StudySession`) ออกไปให้หน้าจอ
- โฟลเดอร์ `ui/` ห้าม import `app.models` หรือ `app.repositories`
- เทียบ enum ด้วย `is` เช่น `status is SessionStatus.FAILED` ห้ามเทียบกับ string
- ผิดพลาดให้ `raise` ลูกของ `AppError` ใส่ `field=` ถ้าเป็นช่องกรอก
- เวลาปัจจุบันใช้ `utcnow()` จาก `app/clock.py` · ตัวเลขตั้งค่าอยู่ใน `Settings`
- ใส่ type hint ทุกตัวแปรและ method · ไม่เขียนบรรทัด comment ตั้งชื่อให้อ่านรู้เรื่องแทน
- ทุก method ในโครงที่ยังว่างจะ `raise NotImplementedError` ให้เจ้าของเขียนแทนที่ ห้ามเปลี่ยนชื่อหรือ parameter โดยไม่บอกกลุ่ม

### `EggTier`

*Enum* · สืบทอดจาก `Enum` · `app/domain/enums.py`

ระดับไข่ 3 ระดับ ยิ่งสูงยิ่งต้องอ่านนานและได้สัตว์หายากขึ้น

**สร้าง:** `EggTier.FRESHMAN`

| ค่า | สร้างยังไง | ความหมาย |
|---|---|---|
| `FRESHMAN` | ค่า `"freshman"` | ไข่รุ่นเรา |
| `SENIOR` | ค่า `"senior"` | ไข่รุ่นพี่ |
| `PROFESSOR` | ค่า `"professor"` | ไข่อาจารย์ (God Egg) |

### `Rarity`

*Enum* · สืบทอดจาก `Enum` · `app/domain/enums.py`

ความหายากของสัตว์แต่ละชนิด

**สร้าง:** `Rarity.COMMON`

| ค่า | สร้างยังไง | ความหมาย |
|---|---|---|
| `COMMON` | ค่า `"common"` | ธรรมดา |
| `RARE` | ค่า `"rare"` | หายาก |
| `EPIC` | ค่า `"epic"` | หายากมาก |
| `LEGENDARY` | ค่า `"legendary"` | ตำนาน |

### `SessionStatus`

*Enum* · สืบทอดจาก `Enum` · `app/domain/enums.py`

สถานะของการอ่านหนึ่งรอบ ตาม state diagram

**สร้าง:** `SessionStatus.RUNNING`

| ค่า | สร้างยังไง | ความหมาย |
|---|---|---|
| `RUNNING` | ค่า `"running"` | กำลังอ่าน นาฬิกาเดินอยู่ |
| `READY_TO_HATCH` | ค่า `"ready_to_hatch"` | หยุดแล้วเกิน 15 นาที รอเลือกไข่ |
| `HATCHED` | ค่า `"hatched"` | ฟักแล้ว ได้สัตว์ |
| `FAILED` | ค่า `"failed"` | หยุดก่อน 15 นาที ไม่ได้ไข่ |
| `ABANDONED` | ค่า `"abandoned"` | ปิดแอปค้างไว้เกิน 6 ชม. |

### `AppError`

*Exception* · สืบทอดจาก `Exception` · `app/errors.py`

แม่ของ error ทุกตัวในแอป หน้าจอจับ AppError แล้วโชว์ message ให้ผู้ใช้

**สร้าง:** `AppError(message, field=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `message` | `str` | ต้องส่งตอนสร้าง | ข้อความที่จะโชว์บนหน้าจอ (ภาษาไทยหรืออังกฤษก็ได้ แต่ต้องอ่านรู้เรื่อง) |
| `field` | `str \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ชื่อช่องที่ผิด เช่น "email" ให้หน้าจอขึ้นสีแดงใต้ช่องนั้น |

### `ValidationError`

*class* · สืบทอดจาก `AppError` · `app/errors.py`

ข้อมูลที่กรอกไม่ถูกต้อง เช่น email ผิดรูปแบบ

**สร้าง:** `ValidationError("ข้อความ", field="email")`

### `AuthError`

*class* · สืบทอดจาก `AppError` · `app/errors.py`

login ไม่ผ่าน หรือยังไม่ได้ login

**สร้าง:** `AuthError("ข้อความ", field="email")`

### `NotFoundError`

*class* · สืบทอดจาก `AppError` · `app/errors.py`

หาข้อมูลไม่เจอ เช่น session_id ไม่มีอยู่

**สร้าง:** `NotFoundError("ข้อความ", field="email")`

### `InvalidStateError`

*class* · สืบทอดจาก `AppError` · `app/errors.py`

ทำผิดลำดับ เช่น hatch ทั้งที่ session ยังไม่ READY_TO_HATCH

**สร้าง:** `InvalidStateError("ข้อความ", field="email")`

### `UserDTO`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ข้อมูลผู้ใช้ที่ส่งให้หน้าจอ (ไม่มี password_hash)

**สร้าง:** `UserDTO(id=..., username=..., email=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | รหัสผู้ใช้ |
| `username` | `str` | ต้องส่งตอนสร้าง | ชื่อที่โชว์ในแอป |
| `email` | `str` | ต้องส่งตอนสร้าง | อีเมล |

### `SpeciesDTO`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ข้อมูลสัตว์หนึ่งชนิด

**สร้าง:** `SpeciesDTO(id=..., code=..., name=..., tier=..., rarity=..., sprite_path=..., description=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | รหัสชนิดสัตว์ |
| `code` | `str` | ต้องส่งตอนสร้าง | รหัสสั้นไม่ซ้ำ เช่น "bug_cat" ใช้ตั้งชื่อไฟล์ sprite |
| `name` | `str` | ต้องส่งตอนสร้าง | ชื่อที่โชว์ |
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ออกจากไข่ระดับไหน |
| `rarity` | `Rarity` | ต้องส่งตอนสร้าง | ความหายาก |
| `sprite_path` | `str` | ต้องส่งตอนสร้าง | path รูปใน assets/sprites |
| `description` | `str` | ต้องส่งตอนสร้าง | คำอธิบายใน Dex |

### `TierInfo`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ข้อมูลไข่หนึ่งระดับ ใช้ในหน้า Egg Rate และ Summary

**สร้าง:** `TierInfo(tier=..., name_th=..., required_minutes=..., rarity_weights=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ระดับ |
| `name_th` | `str` | ต้องส่งตอนสร้าง | ชื่อภาษาไทย เช่น "ไข่รุ่นพี่" |
| `required_minutes` | `int` | ต้องส่งตอนสร้าง | เวลาขั้นต่ำ (นาที) |
| `rarity_weights` | `dict[Rarity, int]` | ต้องส่งตอนสร้าง | โอกาสแต่ละ rarity รวมกันได้ 100 |

### `SessionDTO`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

การอ่านหนึ่งรอบ ตอนเริ่ม/กำลังอ่าน

**สร้าง:** `SessionDTO(id=..., subject=..., started_at=..., status=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | session_id |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชาที่อ่าน |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม (UTC) |
| `status` | `SessionStatus` | ต้องส่งตอนสร้าง | สถานะ |

### `StopResult`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ผลหลังกด Stop

**สร้าง:** `StopResult(session_id=..., status=..., duration_sec=..., unlocked_tiers=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | session ที่หยุด |
| `status` | `SessionStatus` | ต้องส่งตอนสร้าง | FAILED หรือ READY_TO_HATCH |
| `duration_sec` | `int` | ต้องส่งตอนสร้าง | เวลาที่อ่านทั้งหมด (วินาที) |
| `unlocked_tiers` | `list[EggTier]` | ต้องส่งตอนสร้าง | ระดับไข่ที่ปลดล็อก ว่างถ้า FAILED |

### `SummaryDTO`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ข้อมูลหน้า ⑤ Summary

**สร้าง:** `SummaryDTO(session_id=..., subject=..., duration_sec=..., tiers=..., unlocked_tiers=..., best_tier=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | session |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `duration_sec` | `int` | ต้องส่งตอนสร้าง | Total time |
| `tiers` | `list[TierInfo]` | ต้องส่งตอนสร้าง | ไข่ทุกระดับ เอาไว้โชว์ทั้งที่ล็อกและไม่ล็อก |
| `unlocked_tiers` | `list[EggTier]` | ต้องส่งตอนสร้าง | ระดับที่เลือกได้ |
| `best_tier` | `EggTier` | ต้องส่งตอนสร้าง | ระดับสูงสุดที่ปลดล็อก (ใช้ข้อความ You can unlock ...) |

### `PetDTO`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

สัตว์หนึ่งตัวที่ผู้ใช้เลี้ยงอยู่

**สร้าง:** `PetDTO(pet_id=..., species=..., level=..., scale=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `pet_id` | `int` | ต้องส่งตอนสร้าง | รหัส OwnedPet |
| `species` | `SpeciesDTO` | ต้องส่งตอนสร้าง | ชนิด |
| `level` | `int` | ต้องส่งตอนสร้าง | level ปัจจุบัน เริ่มที่ 1 |
| `scale` | `float` | ต้องส่งตอนสร้าง | ขนาดเทียบตัวปกติ 1.0 ถึง 2.0 |

### `HatchResult`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ผลการฟักไข่

**สร้าง:** `HatchResult(session_id=..., tier=..., pet=..., is_new=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | session |
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ไข่ที่เลือก |
| `pet` | `PetDTO` | ต้องส่งตอนสร้าง | สัตว์ที่ได้ (level หลังอัปเดตแล้ว) |
| `is_new` | `bool` | ต้องส่งตอนสร้าง | True = ได้ตัวใหม่, False = ตัวซ้ำ level up |

### `SessionReport`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

รายงานของการอ่านหนึ่งรอบ (Analytics Report)

**สร้าง:** `SessionReport(session_id=..., subject=..., status=..., is_success=..., duration_sec=..., started_at=..., ended_at=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `session_id` | `int` | ต้องส่งตอนสร้าง | session |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `status` | `SessionStatus` | ต้องส่งตอนสร้าง | สถานะสุดท้าย |
| `is_success` | `bool` | ต้องส่งตอนสร้าง | True ถ้า HATCHED |
| `duration_sec` | `int` | ต้องส่งตอนสร้าง | เวลาที่ใช้ |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `ended_at` | `datetime \| None` | ต้องส่งตอนสร้าง | เวลาจบ |
| `tier` | `EggTier \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ไข่ที่เลือก |
| `pet` | `PetDTO \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | สัตว์ที่ได้ None ถ้าไม่สำเร็จ |
| `is_new` | `bool \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ได้ตัวใหม่ไหม |

### `DexEntry`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

หนึ่งช่องใน CPE Dex

**สร้าง:** `DexEntry(species=..., unlocked=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `species` | `SpeciesDTO` | ต้องส่งตอนสร้าง | ชนิดสัตว์ |
| `unlocked` | `bool` | ต้องส่งตอนสร้าง | เคยได้หรือยัง ถ้ายังให้โชว์เป็นเงาดำ |
| `level` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `0` | level ปัจจุบัน 0 ถ้ายังไม่เคยได้ |
| `times_hatched` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `0` | ฟักได้ตัวนี้กี่ครั้ง |
| `first_hatched_at` | `datetime \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ได้ครั้งแรกเมื่อไหร่ |
| `subjects` | `list[str]` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `[]` | วิชาที่อ่านตอนได้ตัวนี้ ไม่ซ้ำกัน |

### `HistoryStats`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

สถิติรวมทุก session

**สร้าง:** `HistoryStats(total_sessions=..., success_count=..., fail_count=..., success_rate=..., total_study_sec=..., weekly_study_sec=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `total_sessions` | `int` | ต้องส่งตอนสร้าง | จำนวนรอบทั้งหมด |
| `success_count` | `int` | ต้องส่งตอนสร้าง | จำนวนรอบที่ฟักสำเร็จ |
| `fail_count` | `int` | ต้องส่งตอนสร้าง | จำนวนรอบที่ไม่สำเร็จ |
| `success_rate` | `float` | ต้องส่งตอนสร้าง | 0.0 ถึง 1.0 |
| `total_study_sec` | `int` | ต้องส่งตอนสร้าง | เวลาอ่านรวม |
| `weekly_study_sec` | `dict[str, int]` | ต้องส่งตอนสร้าง | key = "2026-W39", value = วินาทีที่อ่านในสัปดาห์นั้น |

### `History`

*dataclass (แก้ค่าไม่ได้)* · `app/dto.py`

ข้อมูลหน้า History

**สร้าง:** `History(reports=..., stats=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `reports` | `list[SessionReport]` | ต้องส่งตอนสร้าง | ทุก session เรียงใหม่สุดก่อน |
| `stats` | `HistoryStats` | ต้องส่งตอนสร้าง | สถิติรวม |

<a id="p1"></a>

## P1 · Auth

หน้า ① Sign in / Log in / Sign up · 10 class · 10 ไฟล์

### `AuthProvider`

*abstract class* · `app/services/auth/auth_provider.py`

แม่ของวิธี login ทุกแบบ (abstraction) เพิ่มวิธีใหม่ได้โดยสร้างลูกเพิ่ม

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `name` | `str` | ค่าคงที่ของ class `= "base"` | ชื่อวิธี เช่น "email", "google" |
| `users` | `UserRepository` | ต้องส่งตอนสร้าง | repository ของ user |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `authenticate(payload: dict[str, str])` *abstract* | `User` | ตรวจแล้วคืน User ถ้าไม่ผ่าน raise AuthError |

### `EmailAuthProvider`

*class* · สืบทอดจาก `AuthProvider` · `app/services/auth/email_provider.py`

login ด้วย email + password

**สร้าง:** `EmailAuthProvider(users, hasher)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `name` | `str` | ค่าคงที่ของ class `= "email"` |  |
| `users` | `UserRepository` | ต้องส่งตอนสร้าง |  |
| `hasher` | `PasswordHasher` | ต้องส่งตอนสร้าง | ตัวเช็กรหัสผ่าน |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `authenticate(payload: dict[str, str])` | `User` | payload = {"email", "password"} |

### `GoogleAuthProvider`

*class* · สืบทอดจาก `AuthProvider` · `app/services/auth/google_provider.py`

login ด้วย Google ถ้ายังไม่มี user ให้สร้างใหม่

**สร้าง:** `GoogleAuthProvider(users)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `name` | `str` | ค่าคงที่ของ class `= "google"` |  |
| `users` | `UserRepository` | ต้องส่งตอนสร้าง |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `authenticate(payload: dict[str, str])` | `User` | payload = {"google_id", "email", "name"} จาก page.auth.user |

### `PasswordHasher`

*class* · `app/services/auth/password_hasher.py`

เข้ารหัสผ่านด้วย bcrypt ห้ามเก็บรหัสผ่านจริงลง database

**สร้าง:** `PasswordHasher(rounds=12)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `rounds` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `12` | ความยากของ bcrypt |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `hash(password: str)` | `str` | รหัสผ่าน → hash |
| `verify(password: str, hashed: str)` | `bool` | ตรงกันไหม |

### `CredentialValidator`

*class* · `app/services/auth/credential_validator.py`

เช็กข้อมูลที่กรอกก่อนส่ง คืน dict ชื่อช่อง → ข้อความ error (ว่าง = ผ่าน)

**สร้าง:** `CredentialValidator()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `MIN_PASSWORD_LEN` | `int` | ค่าคงที่ของ class `= 8` | รหัสผ่านสั้นสุด |
| `USERNAME_LEN` | `tuple[int, int]` | ค่าคงที่ของ class `= (3, 32)` | ความยาว username |
| `EMAIL_PATTERN` | `str` | ค่าคงที่ของ class `= r"^[^@\s]+@[^@\s]+\.[^@\s]+$"` | regex email |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `validate_login(email: str, password: str)` | `dict[str, str]` | เช็กว่ากรอกครบ + email ถูกรูปแบบ |
| `validate_signup(username: str, email: str, password: str, confirm: str, accepted_terms: bool)` | `dict[str, str]` | เช็กทุกช่อง + รหัสผ่านตรงกัน + ติ๊ก T&C |

### `RememberMe`

*class* · `app/services/auth/remember_me.py`

จำ user_id ที่ login ล่าสุดไว้ในไฟล์ เปิดแอปครั้งหน้าไม่ต้อง login ใหม่

**สร้าง:** `RememberMe(file_path)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `file_path` | `Path` | ต้องส่งตอนสร้าง | มาจาก Settings.remember_file |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `save(user_id: int)` | `None` | เขียน user_id ลงไฟล์ |
| `load()` | `int \| None` | อ่าน user_id ไม่มีไฟล์คืน None |
| `clear()` | `None` | ลบไฟล์ (ตอน logout) |

### `AuthService`

*class* · `app/services/auth/auth_service.py`

service ของการสมัคร/login/logout ที่หน้าจอเรียกใช้

**สร้าง:** `AuthService(database, settings)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `database` | `Database` | ต้องส่งตอนสร้าง | database |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | ค่าตั้งค่า |
| `hasher` | `PasswordHasher` | สร้างใน `__init__` = `PasswordHasher()` | เข้ารหัส |
| `validator` | `CredentialValidator` | สร้างใน `__init__` = `CredentialValidator()` | เช็กข้อมูล |
| `remember` | `RememberMe` | สร้างใน `__init__` = `RememberMe(Path(settings.remember_file))` | จำ login |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `register(username: str, email: str, password: str, confirm: str, accepted_terms: bool)` | `UserDTO` | สมัคร ถ้าผิด raise ValidationError(field=...) |
| `login(email: str, password: str, remember: bool = True)` | `UserDTO` | login ด้วย email |
| `login_with_google(google_user: dict[str, str])` | `UserDTO` | login ด้วย Google |
| `restore_session()` | `UserDTO \| None` | อ่าน RememberMe แล้วคืน user |
| `logout()` | `None` | ล้าง RememberMe |

### `LoginView`

*class* · สืบทอดจาก `BaseView` · `ui/auth/login_view.py`

หน้า ① มี 2 โหมด login / signup สลับด้วยปุ่มด้านบน (highlight ปุ่มที่เลือก)

**สร้าง:** `LoginView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/login"` |  |
| `requires_login` | `bool` | ค่าคงที่ของ class `= False` |  |
| `mode` | `str` | สร้างใน `__init__` = `"login"` | "login" \| "signup" |
| `email_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` | ช่อง email โหมด login |
| `password_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` | ช่อง password โหมด login |
| `signup_panel` | `SignUpPanel \| None` | สร้างใน `__init__` = `None` | ฟอร์มสมัคร |
| `error_texts` | `dict[str, ft.Text]` | สร้างใน `__init__` = `{}` | ชื่อช่อง → ข้อความ error สีแดง |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า (desktop 2 คอลัมน์, mobile คอลัมน์เดียว) |
| `switch_mode(mode: str)` | `None` | สลับ login / signup |
| `submit()` | `None` | กดปุ่ม Sign in / Log in |
| `on_google_click()` | `None` | เรียก page.login(GoogleOAuthProvider) |
| `on_google_login(e: Any)` | `None` | callback หลัง Google ตอบกลับ |
| `show_errors(errors: dict[str, str])` | `None` | โชว์ error ใต้ช่อง |
| `go_lobby(user: UserDTO)` | `None` | ตั้ง ctx.user แล้วไป /lobby |

### `SignUpPanel`

*class* · สืบทอดจาก `BaseWidget` · `ui/auth/signup_panel.py`

ฟอร์มสมัคร: username, email, password, confirm password, ติ๊ก T&C

**สร้าง:** `SignUpPanel(on_submit, on_show_terms)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `on_submit` | `Callable[[dict[str, Any]], None]` | ต้องส่งตอนสร้าง | ส่งข้อมูลให้ LoginView |
| `on_show_terms` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กดลิงก์อ่าน T&C |
| `username_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` |  |
| `email_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` |  |
| `password_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` |  |
| `confirm_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` |  |
| `terms_checkbox` | `ft.Checkbox \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างฟอร์ม |
| `collect()` | `dict[str, Any]` | รวมค่าทุกช่องเป็น dict key ตรงกับ AuthService.register |

### `TermsDialog`

*class* · `ui/auth/terms_dialog.py`

dialog แสดง Terms and Conditions

**สร้าง:** `TermsDialog(text)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `text` | `str` | ต้องส่งตอนสร้าง | เนื้อหา T&C |
| `_dialog` | `ft.AlertDialog \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `open(page: ft.Page)` | `None` | เปิด |
| `close(page: ft.Page)` | `None` | ปิด |

<a id="p2"></a>

## P2 · Backend core + Data

config, database, models, repositories · 13 class · 12 ไฟล์

### `Settings`

*dataclass* · `app/config.py`

ค่าตั้งค่าของแอปทั้งหมดรวมไว้ที่เดียว ห้าม hard-code ตัวเลขเหล่านี้ในไฟล์อื่น

**สร้าง:** `Settings()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `db_url` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"sqlite:///egg_hatch.db"` | ที่อยู่ database |
| `min_success_minutes` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `15` | อ่านขั้นต่ำกี่นาทีถึงได้ไข่ |
| `abandon_after_hours` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `6` | session ค้างเกินกี่ชม. ถึงนับเป็น ABANDONED |
| `google_client_id` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `""` | จาก Google Cloud Console |
| `google_client_secret` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `""` | จาก Google Cloud Console |
| `remember_file` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `".egg_hatch_login"` | ไฟล์จำการ login ในเครื่อง |
| `species_seed_path` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"seed/species.json"` | ไฟล์รายชื่อสัตว์ |

### `Base`

*class* · สืบทอดจาก `DeclarativeBase` · `app/database.py`

แม่ของ model ทุกตัว (SQLAlchemy 2.0)

### `Database`

*class* · `app/database.py`

ถือ engine และสร้าง db session ให้ service ใช้

**สร้าง:** `Database(url)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `url` | `str` | ต้องส่งตอนสร้าง | มาจาก Settings.db_url |
| `engine` | `Engine` | สร้างใน `__init__` = `create_engine(url)` | ตัวเชื่อมต่อ database |
| `_session_factory` | `sessionmaker` | สร้างใน `__init__` = `sessionmaker(bind=self.engine, expire_on_commit=False)` | โรงงานสร้าง Session |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `create_all()` | `None` | สร้างตารางทั้งหมดถ้ายังไม่มี |
| `session()` | `Session` | เปิด Session ใหม่ ใช้กับ with ... as s: |

### `User`

*SQLAlchemy model* · สืบทอดจาก `Base` · `app/models/user.py`

ตาราง users

**สร้าง:** `User(username=..., email=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | `mapped_column(primary_key=True)` | รหัสผู้ใช้ |
| `username` | `str` | `mapped_column(String(32), unique=True)` | ชื่อในแอป 3-32 ตัว |
| `email` | `str` | `mapped_column(String(255), unique=True)` | อีเมล เก็บเป็นตัวเล็ก |
| `password_hash` | `str \| None` | `mapped_column(String(255), default=None)` | None ถ้าสมัครด้วย Google |
| `google_id` | `str \| None` | `mapped_column(String(64), unique=True, default=None)` | sub จาก Google |
| `created_at` | `datetime` | `mapped_column(default=utcnow)` | วันสมัคร |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `to_dto()` | `UserDTO` | แปลงเป็น UserDTO |

### `Species`

*SQLAlchemy model* · สืบทอดจาก `Base` · `app/models/species.py`

ตาราง species สัตว์ทุกชนิดในเกม (seed จาก species.json ของ P5)

**สร้าง:** `Species(code=..., name=..., tier=..., rarity=..., sprite_path=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | `mapped_column(primary_key=True)` | รหัส |
| `code` | `str` | `mapped_column(String(32), unique=True)` | รหัสสั้น |
| `name` | `str` | `mapped_column(String(64))` | ชื่อ |
| `tier` | `EggTier` | `mapped_column(SAEnum(EggTier))` | ระดับไข่ |
| `rarity` | `Rarity` | `mapped_column(SAEnum(Rarity))` | ความหายาก |
| `sprite_path` | `str` | `mapped_column(String(255))` | path รูป |
| `description` | `str` | `mapped_column(String(500), default="")` | คำอธิบาย |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `to_dto()` | `SpeciesDTO` | แปลงเป็น SpeciesDTO |

### `StudySession`

*SQLAlchemy model* · สืบทอดจาก `Base` · `app/models/study_session.py`

ตาราง study_sessions การอ่านหนึ่งรอบ · P2 สร้าง column, P6 เขียน method (encapsulation: เปลี่ยน status ผ่าน method เท่านั้น)

**สร้าง:** `StudySession(user_id=..., subject=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | `mapped_column(primary_key=True)` | session_id |
| `user_id` | `int` | `mapped_column(ForeignKey("users.id"))` | เจ้าของ |
| `subject` | `str` | `mapped_column(String(100))` | วิชาที่อ่าน |
| `started_at` | `datetime` | `mapped_column(default=utcnow)` | เวลาเริ่ม |
| `ended_at` | `datetime \| None` | `mapped_column(default=None)` | เวลาหยุด |
| `duration_sec` | `int` | `mapped_column(default=0)` | เวลาที่อ่าน คำนวณตอน stop |
| `status` | `SessionStatus` | `mapped_column(SAEnum(SessionStatus), default=SessionStatus.RUNNING)` | สถานะ |
| `chosen_tier` | `EggTier \| None` | `mapped_column(SAEnum(EggTier), default=None)` | ไข่ที่เลือกตอน hatch |
| `species_id` | `int \| None` | `mapped_column(ForeignKey("species.id"), default=None)` | สัตว์ที่ได้ |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `elapsed_sec(now: datetime)` | `int` | [P6] วินาทีตั้งแต่ started_at ถึง now |
| `stop(now: datetime, min_success_sec: int)` | `SessionStatus` | [P6] ตั้ง ended_at, duration_sec แล้วเปลี่ยนเป็น FAILED หรือ READY_TO_HATCH · ถ้าไม่ได้ RUNNING ให้ raise InvalidStateError |
| `abandon(now: datetime)` | `None` | [P6] เปลี่ยน RUNNING เป็น ABANDONED |
| `can_hatch()` | `bool` | [P6] True ถ้า status เป็น READY_TO_HATCH |
| `mark_hatched(tier: EggTier, species_id: int)` | `None` | [P6] บันทึกไข่ที่เลือก + สัตว์ที่ได้ เปลี่ยนเป็น HATCHED |
| `is_success()` | `bool` | [P6] True ถ้า HATCHED |
| `to_dto()` | `SessionDTO` | [P6] แปลงเป็น SessionDTO |

### `OwnedPet`

*SQLAlchemy model* · สืบทอดจาก `Base` · `app/models/owned_pet.py`

ตาราง owned_pets สัตว์ที่ผู้ใช้มี หนึ่งชนิดมีได้แถวเดียวต่อคน · P2 สร้าง column, P8 เขียน method

**สร้าง:** `OwnedPet(user_id=..., species_id=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | `mapped_column(primary_key=True)` | pet_id |
| `user_id` | `int` | `mapped_column(ForeignKey("users.id"))` | เจ้าของ |
| `species_id` | `int` | `mapped_column(ForeignKey("species.id"))` | ชนิด |
| `level` | `int` | `mapped_column(default=1)` | level เริ่ม 1 |
| `times_hatched` | `int` | `mapped_column(default=1)` | ฟักได้ตัวนี้กี่ครั้ง |
| `first_hatched_at` | `datetime` | `mapped_column(default=utcnow)` | ได้ครั้งแรก |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `level_up(policy: PetLevelPolicy)` | `None` | [P8] เพิ่ม times_hatched และ level ตาม policy |
| `scale(policy: PetLevelPolicy)` | `float` | [P8] ขนาดตาม level |
| `to_dto(species: SpeciesDTO, policy: PetLevelPolicy)` | `PetDTO` | [P8] แปลงเป็น PetDTO |

### `BaseRepository`

*class* · สืบทอดจาก `Generic[T]` · `app/repositories/base_repository.py`

แม่ของ repository ทุกตัว รวมคำสั่ง database ที่ใช้บ่อย (inheritance + generic)

**สร้าง:** `BaseRepository(db)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `model` | `type` | ค่าคงที่ของ class `= Base` | model ที่ repository นี้ดูแล ลูกต้อง override |
| `db` | `Session` | ต้องส่งตอนสร้าง | SQLAlchemy Session ที่ service ส่งมา |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `get(id: int)` | `T \| None` | หาแถวตาม id |
| `get_or_raise(id: int)` | `T` | เหมือน get แต่ raise NotFoundError ถ้าไม่เจอ |
| `add(obj: T)` | `T` | เพิ่มแล้ว flush ให้ได้ id |
| `list(**filters: Any)` | `list[T]` | หาหลายแถว เช่น list(user_id=1) |
| `delete(obj: T)` | `None` | ลบ |
| `commit()` | `None` | บันทึกลง database |

### `UserRepository`

*class* · สืบทอดจาก `BaseRepository[User]` · `app/repositories/user_repository.py`

คำสั่ง database ของ User

**สร้าง:** `UserRepository(db)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `model` | `type` | ค่าคงที่ของ class `= User` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `get_by_email(email: str)` | `User \| None` | หาจาก email (แปลงตัวเล็กก่อน) |
| `get_by_google_id(google_id: str)` | `User \| None` | หาจาก Google |
| `exists_username(username: str)` | `bool` | เช็กชื่อซ้ำ |

### `SessionRepository`

*class* · สืบทอดจาก `BaseRepository[StudySession]` · `app/repositories/session_repository.py`

คำสั่ง database ของ StudySession

**สร้าง:** `SessionRepository(db)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `model` | `type` | ค่าคงที่ของ class `= StudySession` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `get_running(user_id: int)` | `StudySession \| None` | session ที่ RUNNING อยู่ (มีได้แค่อันเดียว) |
| `list_by_user(user_id: int)` | `list[StudySession]` | ทุก session ใหม่สุดก่อน |
| `list_stale_running(before: datetime)` | `list[StudySession]` | RUNNING ที่เริ่มก่อน before |
| `list_subjects_for_species(user_id: int, species_id: int)` | `list[str]` | วิชาที่อ่านตอนได้สัตว์ชนิดนี้ (ใช้ใน Dex) |

### `PetRepository`

*class* · สืบทอดจาก `BaseRepository[OwnedPet]` · `app/repositories/pet_repository.py`

คำสั่ง database ของ OwnedPet

**สร้าง:** `PetRepository(db)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `model` | `type` | ค่าคงที่ของ class `= OwnedPet` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `get_owned(user_id: int, species_id: int)` | `OwnedPet \| None` | เช็กว่ามีตัวนี้แล้วหรือยัง |
| `list_by_user(user_id: int)` | `list[OwnedPet]` | สัตว์ทั้งหมดของผู้ใช้ |

### `SpeciesRepository`

*class* · สืบทอดจาก `BaseRepository[Species]` · `app/repositories/species_repository.py`

คำสั่ง database ของ Species

**สร้าง:** `SpeciesRepository(db)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `model` | `type` | ค่าคงที่ของ class `= Species` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `list_by_tier(tier: EggTier)` | `list[Species]` | สัตว์ทุกตัวของไข่ระดับนี้ (pool สำหรับสุ่ม) |
| `get_by_code(code: str)` | `Species \| None` | หาจาก code |
| `list_all()` | `list[Species]` | ทุกชนิด เรียงตาม tier แล้ว rarity |

### `UnitOfWork`

*class* · `app/services/unit_of_work.py`

เปิด db session หนึ่งอัน แล้วสร้าง repository ทุกตัวให้ service ใช้ร่วมกัน ใช้กับ with

**สร้าง:** `UnitOfWork(database)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `database` | `Database` | ต้องส่งตอนสร้าง | Database ของแอป |
| `db` | `Session \| None` | สร้างใน `__init__` = `None` | Session ที่เปิดอยู่ |
| `users` | `UserRepository \| None` | สร้างใน `__init__` = `None` | สร้างตอน __enter__ |
| `sessions` | `SessionRepository \| None` | สร้างใน `__init__` = `None` |  |
| `pets` | `PetRepository \| None` | สร้างใน `__init__` = `None` |  |
| `species` | `SpeciesRepository \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `__enter__()` | `UnitOfWork` | เปิด Session + สร้าง repository |
| `__exit__(*exc: Any)` | `None` | commit ถ้าไม่มี error, rollback ถ้ามี แล้วปิด |

<a id="p3"></a>

## P3 · Frontend core + How to

AppContext, Navigator, BaseView, widgets · 12 class · 8 ไฟล์

### `BaseWidget`

*abstract class* · `ui/core/base_widget.py`

แม่ของ widget ทุกตัวที่เราสร้างเอง ใช้ composition: ห่อ Flet control ไว้ข้างใน แล้วคืนผ่าน build()

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_control` | `ft.Control \| None` | สร้างใน `__init__` = `None` | cache ของ control ที่ build แล้ว |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` *abstract* | `ft.Control` | สร้าง Flet control |
| `control` *property* | `ft.Control` | build ครั้งแรกแล้วเก็บไว้ ครั้งต่อไปคืนตัวเดิม |
| `refresh()` | `None` | สั่ง update() หลังเปลี่ยนค่า |

### `BaseView`

*abstract class* · `ui/core/base_view.py`

แม่ของทุกหน้าจอ Navigator เรียก to_view() ตอนเปลี่ยนหน้า (inheritance + polymorphism)

**สร้าง:** `BaseView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/"` | path ของหน้า เช่น "/lobby" |
| `requires_login` | `bool` | ค่าคงที่ของ class `= True` | False เฉพาะหน้า login |
| `ctx` | `AppContext` | ต้องส่งตอนสร้าง | ของกลางทั้งแอป |
| `params` | `dict[str, Any]` | สร้างใน `__init__` = `dict(params)` | ค่าที่ส่งมากับ nav.go เช่น session_id |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` *abstract* | `ft.Control` | สร้างเนื้อหาของหน้า |
| `on_enter()` | `None` | เรียกหลังหน้าแสดง เช่น โหลดข้อมูล เริ่ม timer |
| `on_leave()` | `None` | เรียกก่อนออกจากหน้า เช่น หยุด timer |
| `show_error(error: AppError)` | `None` | โชว์ SnackBar ข้อความ error |
| `to_view()` | `ft.View` | ห่อ build() เป็น ft.View |

### `Navigator`

*class* · `ui/core/navigator.py`

ตัวสลับหน้า ถ้ายังไม่ login จะเด้งไป /login

**สร้าง:** `Navigator(ctx)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `ctx` | `AppContext` | ต้องส่งตอนสร้าง | ของกลาง |
| `routes` | `dict[str, type[BaseView]]` | สร้างใน `__init__` = `{}` | route → class ของหน้า |
| `current` | `BaseView \| None` | สร้างใน `__init__` = `None` | หน้าที่เปิดอยู่ |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `register(view_cls: type[BaseView])` | `None` | ลงทะเบียนหน้า |
| `start()` | `None` | เปิดหน้าแรก: /lobby ถ้า login แล้ว ไม่งั้น /login |
| `go(route: str, **params: Any)` | `None` | ไปหน้าใหม่ (เรียก on_leave ของหน้าเก่า on_enter ของหน้าใหม่) |
| `back()` | `None` | กลับหน้าก่อน |

### `AppContext`

*class* · `ui/core/app_context.py`

ของกลางที่ทุกหน้าใช้: page, ผู้ใช้ปัจจุบัน, service ทุกตัว หน้าจอเข้าถึง backend ผ่านที่นี่เท่านั้น

**สร้าง:** `AppContext(page, settings, database)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `page` | `ft.Page` | ต้องส่งตอนสร้าง | หน้าต่าง Flet |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | ค่าตั้งค่า |
| `database` | `Database` | ต้องส่งตอนสร้าง | database |
| `user` | `UserDTO \| None` | สร้างใน `__init__` = `None` | ผู้ใช้ที่ login อยู่ |
| `auth` | `AuthService` | สร้างใน `__init__` = `AuthService(database, settings)` | P1 |
| `tiers` | `TierService` | สร้างใน `__init__` = `TierService()` | P5 |
| `focus` | `FocusSessionService` | สร้างใน `__init__` = `FocusSessionService(database, settings)` | P6 |
| `summary` | `SummaryService` | สร้างใน `__init__` = `SummaryService(database)` | P7 |
| `hatch` | `HatchService` | สร้างใน `__init__` = `HatchService(database)` | P8 |
| `sanctuary` | `SanctuaryService` | สร้างใน `__init__` = `SanctuaryService(database)` | P4 |
| `dex` | `DexService` | สร้างใน `__init__` = `DexService(database)` | P9 |
| `analytics` | `AnalyticsService` | สร้างใน `__init__` = `AnalyticsService(database)` | P7 + P9 |
| `sound` | `SoundManager` | สร้างใน `__init__` = `SoundManager(page)` | เสียง |
| `nav` | `Navigator` | สร้างใน `__init__` = `Navigator(self)` | ตัวสลับหน้า |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `create(page: ft.Page, settings: Settings)` *classmethod* | `AppContext` | สร้าง Database, create_all, seed สัตว์ แล้วคืน AppContext |
| `require_user()` | `UserDTO` | คืน user ถ้าไม่มีให้ raise AuthError |

### `Theme`

*class* · `ui/core/theme.py`

สีและฟอนต์ของแอป ใช้ค่าจากที่นี่ห้ามใส่รหัสสีเองในหน้าอื่น

**สร้าง:** `Theme()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `PRIMARY` | `str` | ค่าคงที่ของ class `= "#2F5BD8"` | สีน้ำเงินหลัก (ปุ่ม, หัวข้อ) |
| `ACCENT` | `str` | ค่าคงที่ของ class `= "#F2913A"` | สีส้ม (สัตว์, highlight) |
| `BACKGROUND` | `str` | ค่าคงที่ของ class `= "#FFFFFF"` | พื้นหลัง |
| `TEXT` | `str` | ค่าคงที่ของ class `= "#1D2333"` | ตัวอักษร |
| `ERROR` | `str` | ค่าคงที่ของ class `= "#D2412F"` | ข้อความ error |
| `FONT_FAMILY` | `str` | ค่าคงที่ของ class `= "Mali"` | ฟอนต์หลัก |
| `MOBILE_BREAKPOINT` | `int` | ค่าคงที่ของ class `= 600` | กว้างน้อยกว่านี้ใช้ layout มือถือ |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `apply(page: ft.Page)` *classmethod* | `None` | ตั้งฟอนต์และสีให้ page |
| `is_mobile(page: ft.Page)` *classmethod* | `bool` | True ถ้าจอแคบกว่า MOBILE_BREAKPOINT |

### `SoundManager`

*class* · `ui/core/sound_manager.py`

เล่นเสียง SFX (ใช้ package flet-audio)

**สร้าง:** `SoundManager(page, muted=False)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `page` | `ft.Page` | ต้องส่งตอนสร้าง | หน้าต่าง |
| `muted` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `False` | ปิดเสียงอยู่ไหม |
| `_sounds` | `dict[str, Any]` | สร้างใน `__init__` = `{}` | ชื่อเสียง → ตัวเล่นเสียง |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `load(name: str, path: str)` | `None` | โหลดไฟล์เสียง เช่น load("tada", "sfx/tada.mp3") |
| `play(name: str)` | `None` | เล่นเสียง ถ้า muted ไม่ต้องเล่น |
| `toggle_mute()` | `bool` | สลับเปิด/ปิด คืนค่าใหม่ |

### `PixelButton`

*class* · สืบทอดจาก `BaseWidget` · `ui/core/widgets.py`

ปุ่มสไตล์เดียวกันทั้งแอป

**สร้าง:** `PixelButton(text, on_click, variant="primary", icon=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `text` | `str` | ต้องส่งตอนสร้าง | ข้อความบนปุ่ม |
| `on_click` | `Callable[[], None]` | ต้องส่งตอนสร้าง | ฟังก์ชันตอนกด |
| `variant` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"primary"` | "primary" \| "secondary" \| "danger" |
| `icon` | `str \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ไอคอน |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างปุ่ม |

### `Panel`

*class* · สืบทอดจาก `BaseWidget` · `ui/core/widgets.py`

กรอบ panel มีหัวข้อ + ปุ่มปิด X (Index, How to, Egg rate ใช้ตัวนี้)

**สร้าง:** `Panel(title, content, on_close=None, visible=True)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `title` | `str` | ต้องส่งตอนสร้าง | หัวข้อ panel |
| `content` | `ft.Control` | ต้องส่งตอนสร้าง | เนื้อหาข้างใน |
| `on_close` | `Callable[[], None] \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ถ้ามี จะโชว์ปุ่ม X |
| `visible` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `True` | เปิดอยู่ไหม |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างกรอบ |
| `open()` | `None` | โชว์ |
| `close()` | `None` | ซ่อน |

### `ScrollPanel`

*class* · สืบทอดจาก `Panel` · `ui/core/widgets.py`

Panel ที่เนื้อหาเลื่อนได้ (scrollbar ตาม wireframe)

**สร้าง:** `ScrollPanel(title, content, on_close=None, visible=True, max_height=400)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `title` | `str` | ต้องส่งตอนสร้าง |  |
| `content` | `ft.Control` | ต้องส่งตอนสร้าง |  |
| `on_close` | `Callable[[], None] \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` |  |
| `visible` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `True` |  |
| `max_height` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `400` | สูงสุดก่อนเริ่ม scroll |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง panel ที่มี scroll |

### `ConfirmDialog`

*class* · `ui/core/widgets.py`

กล่องถาม YES / NO เช่น "Are you sure to stop?"

**สร้าง:** `ConfirmDialog(title, on_yes, on_no=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `title` | `str` | ต้องส่งตอนสร้าง | คำถาม |
| `on_yes` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กด YES |
| `on_no` | `Callable[[], None] \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | กด NO (ปกติแค่ปิด) |
| `_dialog` | `ft.AlertDialog \| None` | สร้างใน `__init__` = `None` | dialog ที่สร้างแล้ว |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `open(page: ft.Page)` | `None` | เปิด dialog |
| `close(page: ft.Page)` | `None` | ปิด dialog |

### `HowToSlide`

*dataclass (แก้ค่าไม่ได้)* · `ui/howto/howto_panel.py`

หนึ่งหน้าของ How to Play

**สร้าง:** `HowToSlide(image_path=..., text=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `image_path` | `str` | ต้องส่งตอนสร้าง | รูปอธิบาย |
| `text` | `str` | ต้องส่งตอนสร้าง | คำอธิบาย |

### `HowToPanel`

*class* · สืบทอดจาก `BaseWidget` · `ui/howto/howto_panel.py`

panel How to Play แบบ slideshow มีจุดบอกหน้า + ปุ่ม next + ปุ่มปิด

**สร้าง:** `HowToPanel(slides, on_close)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `slides` | `list[HowToSlide]` | ต้องส่งตอนสร้าง | หน้าทั้งหมด |
| `on_close` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กดปิด |
| `current_index` | `int` | สร้างใน `__init__` = `0` | หน้าที่โชว์อยู่ เริ่ม 0 |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง panel |
| `next()` | `None` | หน้าถัดไป (หน้าสุดท้ายแล้วไม่ต้องไปต่อ) |
| `prev()` | `None` | หน้าก่อน |
| `show(index: int)` | `None` | ไปหน้าที่ index |

<a id="p4"></a>

## P4 · Department Sanctuary

หน้า ② Lobby ห้องภาคคอม · 4 class · 4 ไฟล์

### `SanctuaryService`

*class* · `app/services/sanctuary_service.py`

ดึงสัตว์ทั้งหมดของผู้ใช้ไปโชว์ในห้องภาค

**สร้าง:** `SanctuaryService(database)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `database` | `Database` | ต้องส่งตอนสร้าง | database |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` | ใช้คำนวณ scale |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `list_pets(user_id: int)` | `list[PetDTO]` | สัตว์ทุกตัว + level + scale |

### `PetSprite`

*class* · `ui/lobby/pet_sprite.py`

สัตว์หนึ่งตัวที่เดินดุ๊กดิ๊กในห้อง เดินไปจุดสุ่มแล้วหยุดพัก

**สร้าง:** `PetSprite(pet, x, y, speed=40.0)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `pet` | `PetDTO` | ต้องส่งตอนสร้าง | ข้อมูลสัตว์ |
| `x` | `float` | ต้องส่งตอนสร้าง | ตำแหน่งแนวนอน (px) |
| `y` | `float` | ต้องส่งตอนสร้าง | ตำแหน่งแนวตั้ง (px) |
| `BASE_SIZE` | `int` | ค่าคงที่ของ class `= 64` | ขนาดตอน level 1 |
| `speed` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `40.0` | px ต่อวินาที |
| `target_x` | `float` | สร้างใน `__init__` = `x` | จุดที่กำลังเดินไป |
| `target_y` | `float` | สร้างใน `__init__` = `y` |  |
| `rest_sec` | `float` | สร้างใน `__init__` = `0.0` | เหลือเวลาพักกี่วินาที |
| `facing_left` | `bool` | สร้างใน `__init__` = `False` | หันซ้ายไหม (ใช้กลับรูป) |
| `image` | `ft.Image \| None` | สร้างใน `__init__` = `None` | รูปใน Stack |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `size` *property* | `float` | BASE_SIZE × pet.scale |
| `build()` | `ft.Control` | สร้าง ft.Image วางตำแหน่ง left/top |
| `choose_target(width: float, height: float)` | `None` | สุ่มจุดใหม่ในห้อง |
| `update(dt: float, width: float, height: float)` | `None` | ขยับตาม speed ถึงจุดแล้วพัก 1-3 วิ แล้วสุ่มใหม่ |
| `on_click(e: Any)` | `None` | โชว์ชื่อ + level |

### `SanctuaryScene`

*class* · สืบทอดจาก `BaseWidget` · `ui/lobby/sanctuary_scene.py`

ฉากห้องภาค: รูปพื้นหลัง + สัตว์ทุกตัว อัปเดตทุก tick

**สร้าง:** `SanctuaryScene(width, height, fps=20)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `width` | `float` | ต้องส่งตอนสร้าง | กว้าง |
| `height` | `float` | ต้องส่งตอนสร้าง | สูง |
| `fps` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `20` | อัปเดตกี่ครั้งต่อวินาที |
| `sprites` | `list[PetSprite]` | สร้างใน `__init__` = `[]` | สัตว์ในห้อง |
| `running` | `bool` | สร้างใน `__init__` = `False` | loop ทำงานอยู่ไหม |
| `stack` | `ft.Stack \| None` | สร้างใน `__init__` = `None` | ft.Stack ที่วางสัตว์ |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง Stack + พื้นหลัง |
| `load(pets: list[PetDTO])` | `None` | สร้าง PetSprite จาก pets วางตำแหน่งสุ่ม |
| `start(page: ft.Page)` | `None` | เริ่ม loop ด้วย page.run_task |
| `stop()` | `None` | หยุด loop |
| `tick(dt: float)` | `None` | เรียก update ของทุก sprite แล้ว refresh |

### `LobbyView`

*class* · สืบทอดจาก `BaseView` · `ui/lobby/lobby_view.py`

หน้า ② Main Lobby: ห้องภาค + ปุ่ม Index, How to, History, Start Focus

**สร้าง:** `LobbyView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/lobby"` |  |
| `scene` | `SanctuaryScene \| None` | สร้างใน `__init__` = `None` | ฉากห้องภาค |
| `howto` | `HowToPanel \| None` | สร้างใน `__init__` = `None` | panel How to (ของ P3) |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | โหลด list_pets แล้ว scene.start |
| `on_leave()` | `None` | scene.stop |
| `open_index()` | `None` | ไป /dex |
| `open_history()` | `None` | ไป /history |
| `open_howto()` | `None` | เปิด HowToPanel |
| `start_focus()` | `None` | ไป /setup |

<a id="p5"></a>

## P5 · Set up + Egg domain

หน้า ③ Set up · ระบบไข่ 3 tier · 10 class · 7 ไฟล์

### `Egg`

*abstract class* · `app/domain/eggs.py`

แม่ของไข่ทุกระดับ ลูกต้องบอกเวลาขั้นต่ำและโอกาสแต่ละ rarity (abstraction + polymorphism)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.FRESHMAN` | ระดับ ลูก override |
| `name_th` | `str` | ค่าคงที่ของ class `= ""` | ชื่อภาษาไทย |
| `image_path` | `str` | ค่าคงที่ของ class `= ""` | รูปไข่ |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `required_minutes()` *abstract* | `int` | เวลาขั้นต่ำ |
| `rarity_weights()` *abstract* | `dict[Rarity, int]` | โอกาสแต่ละ rarity รวม 100 |
| `is_unlocked(duration_sec: int)` | `bool` | duration_sec ≥ required_minutes × 60 |
| `roll(pool: list[Species], gacha: GachaMachine)` | `Species` | สุ่ม rarity แล้วสุ่มสัตว์จาก pool |
| `to_tier_info()` | `TierInfo` | แปลงเป็น TierInfo |

### `FreshmanEgg`

*class* · สืบทอดจาก `Egg` · `app/domain/eggs.py`

ไข่รุ่นเรา 15 นาที

**สร้าง:** `FreshmanEgg()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.FRESHMAN` |  |
| `name_th` | `str` | ค่าคงที่ของ class `= "ไข่รุ่นเรา"` |  |
| `image_path` | `str` | ค่าคงที่ของ class `= "eggs/freshman.png"` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `required_minutes()` *เขียนให้แล้ว* | `int` | 15 |
| `rarity_weights()` *เขียนให้แล้ว* | `dict[Rarity, int]` | 70 / 25 / 5 / 0 |

### `SeniorEgg`

*class* · สืบทอดจาก `Egg` · `app/domain/eggs.py`

ไข่รุ่นพี่ 30 นาที

**สร้าง:** `SeniorEgg()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.SENIOR` |  |
| `name_th` | `str` | ค่าคงที่ของ class `= "ไข่รุ่นพี่"` |  |
| `image_path` | `str` | ค่าคงที่ของ class `= "eggs/senior.png"` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `required_minutes()` *เขียนให้แล้ว* | `int` | 30 |
| `rarity_weights()` *เขียนให้แล้ว* | `dict[Rarity, int]` | 40 / 40 / 17 / 3 |

### `ProfessorEgg`

*class* · สืบทอดจาก `Egg` · `app/domain/eggs.py`

ไข่อาจารย์ (God Egg) 60 นาที

**สร้าง:** `ProfessorEgg()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.PROFESSOR` |  |
| `name_th` | `str` | ค่าคงที่ของ class `= "ไข่อาจารย์"` |  |
| `image_path` | `str` | ค่าคงที่ของ class `= "eggs/professor.png"` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `required_minutes()` *เขียนให้แล้ว* | `int` | 60 |
| `rarity_weights()` *เขียนให้แล้ว* | `dict[Rarity, int]` | 10 / 40 / 35 / 15 |

### `EggFactory`

*class* · `app/domain/egg_factory.py`

สร้าง Egg จาก EggTier และบอกว่าเวลาเท่านี้ปลดล็อกไข่อะไรบ้าง

**สร้าง:** `EggFactory()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_registry` | `dict[EggTier, type[Egg]]` | สร้างใน `__init__` = `{EggTier.FRESHMAN: FreshmanEgg, EggTier.SENIOR: SeniorEgg, EggTier.PROFESSOR: ProfessorEgg}` | tier → class |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `create(tier: EggTier)` | `Egg` | สร้างไข่ |
| `all()` | `list[Egg]` | ไข่ทุกระดับ เรียงต่ำไปสูง |
| `unlocked_for(duration_sec: int)` | `list[Egg]` | ไข่ที่ปลดล็อก |
| `best_for(duration_sec: int)` | `Egg \| None` | ไข่สูงสุดที่ปลดล็อก |

### `TierService`

*class* · `app/services/tier_service.py`

ข้อมูลไข่ทุกระดับให้หน้า Egg Rate

**สร้าง:** `TierService(factory=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `factory` | `EggFactory \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ถ้าไม่ส่งมาให้สร้าง EggFactory() เอง |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `list_tiers()` | `list[TierInfo]` | ทุกระดับ เรียงต่ำไปสูง |

### `SpeciesSeeder`

*class* · `app/domain/species_seeder.py`

อ่าน seed/species.json แล้วใส่ตาราง species (เพิ่มเฉพาะ code ที่ยังไม่มี)

**สร้าง:** `SpeciesSeeder(path)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `path` | `Path` | ต้องส่งตอนสร้าง | ไฟล์ json |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `load_json()` | `list[dict[str, str]]` | อ่านไฟล์ |
| `seed(repo: SpeciesRepository)` | `int` | ใส่ลง database คืนจำนวนที่เพิ่ม |

### `SubjectPicker`

*class* · สืบทอดจาก `BaseWidget` · `ui/setup/subject_picker.py`

ช่องใส่ชื่อวิชา + ชิปวิชาที่เคยอ่านล่าสุดให้กดเลือกเร็ว

**สร้าง:** `SubjectPicker(recent_subjects=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `recent_subjects` | `list[str]` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `[]` | วิชาล่าสุด ไม่เกิน 5 |
| `field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` | ช่องกรอก |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `value` *property* | `str` | ชื่อวิชาที่กรอก ตัดช่องว่างหัวท้ายแล้ว |

### `EggRatePanel`

*class* · สืบทอดจาก `BaseWidget` · `ui/setup/egg_rate_panel.py`

panel Egg Rate: แต่ละระดับใช้กี่นาที โอกาสได้สัตว์แต่ละ rarity

**สร้าง:** `EggRatePanel(tiers, on_close)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tiers` | `list[TierInfo]` | ต้องส่งตอนสร้าง | ข้อมูลไข่ |
| `on_close` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กดปิด |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง ScrollPanel |
| `render_tier(info: TierInfo)` | `ft.Control` | หนึ่งแถว |

### `SetupView`

*class* · สืบทอดจาก `BaseView` · `ui/setup/setup_view.py`

หน้า ③ Set up: ปุ่ม BACK, รูปไข่, ใส่วิชา, START, ปุ่ม See egg rate

**สร้าง:** `SetupView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/setup"` |  |
| `subject_picker` | `SubjectPicker \| None` | สร้างใน `__init__` = `None` |  |
| `egg_rate_panel` | `EggRatePanel \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า (desktop โชว์ egg rate ข้าง ๆ, mobile เปิดเป็น panel) |
| `toggle_egg_rate()` | `None` | เปิด/ปิด panel |
| `start()` | `None` | ctx.focus.start แล้วไป /focus พร้อม session_id |

<a id="p6"></a>

## P6 · Focus session + CPEGO

หน้า ④ ฟักไข่ · นาฬิกา + แชทบอท · 7 class · 6 ไฟล์

> มี method ที่ต้องเขียนในไฟล์ของคนอื่นด้วย: `StudySession` (app/models/study_session.py) ดู method ที่ขึ้นต้นด้วย **[P6]**

### `FocusSessionService`

*class* · `app/services/focus_service.py`

เริ่ม / ดูเวลา / หยุด การอ่าน เวลาคิดจาก started_at ใน database เสมอ

**สร้าง:** `FocusSessionService(database, settings)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `database` | `Database` | ต้องส่งตอนสร้าง | database |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | min_success_minutes, abandon_after_hours |
| `factory` | `EggFactory` | สร้างใน `__init__` = `EggFactory()` | ใช้หา unlocked_tiers |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `start(user_id: int, subject: str)` | `SessionDTO` | สร้าง RUNNING ถ้ามี RUNNING อยู่แล้ว raise InvalidStateError, subject ว่าง raise ValidationError |
| `get_running(user_id: int)` | `SessionDTO \| None` | session ที่ค้างอยู่ (เปิดแอปมาแล้วอ่านต่อได้) |
| `elapsed(session_id: int)` | `int` | วินาทีที่อ่านไปแล้ว |
| `stop(session_id: int)` | `StopResult` | หยุดและตัดสินผล |
| `abandon_stale()` | `int` | เปลี่ยน session ค้างเกินกำหนดเป็น ABANDONED คืนจำนวน |

### `StopwatchTimer`

*class* · `ui/focus/stopwatch_timer.py`

นาฬิกานับขึ้น tick ทุก interval_sec แล้วเรียก on_tick(elapsed_sec)

**สร้าง:** `StopwatchTimer(started_at, on_tick, interval_sec=1.0)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่มจาก SessionDTO |
| `on_tick` | `Callable[[int], None]` | ต้องส่งตอนสร้าง | เรียกทุก tick |
| `interval_sec` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1.0` | ระยะห่าง tick |
| `running` | `bool` | สร้างใน `__init__` = `False` | เดินอยู่ไหม |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `start(page: ft.Page)` | `None` | เริ่ม loop ด้วย page.run_task |
| `stop()` | `None` | หยุด |
| `elapsed_sec` *property* | `int` | now − started_at |
| `format(seconds: int)` *staticmethod* | `str` | 67:07 (นาที:วินาที) นาทีเกิน 99 ได้ |

### `EggView`

*class* · สืบทอดจาก `BaseWidget` · `ui/focus/egg_view.py`

รูปไข่กลางจอ เปลี่ยนรูปตามระดับที่ปลดล็อกแล้ว

**สร้าง:** `EggView(tier=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | None = ยังไม่ถึง 15 นาที |
| `image` | `ft.Image \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `set_tier(tier: EggTier \| None)` | `None` | เปลี่ยนรูป |
| `wobble()` | `None` | ไข่ขยับตอนปลดล็อกระดับใหม่ |

### `CpegoMessage`

*dataclass (แก้ค่าไม่ได้)* · `ui/focus/cpego_bot.py`

ข้อความหนึ่งอันในแชท CPEGO

**สร้าง:** `CpegoMessage(text=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `text` | `str` | ต้องส่งตอนสร้าง | ข้อความ |
| `kind` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"info"` | "greeting" \| "milestone" \| "info" |
| `created_at` | `datetime` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `utcnow()` | เวลาส่ง |

### `CpegoBot`

*class* · `ui/focus/cpego_bot.py`

บอทแชท ส่งข้อความเมื่ออ่านครบแต่ละ milestone (ส่งครั้งเดียวต่อ milestone)

**สร้าง:** `CpegoBot(tiers)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tiers` | `list[TierInfo]` | ต้องส่งตอนสร้าง | เอา required_minutes มาเป็น milestone |
| `_sent_minutes` | `set[int]` | สร้างใน `__init__` = `set()` | milestone ที่ส่งไปแล้ว |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `greeting(subject: str)` | `CpegoMessage` | ข้อความทักตอนเริ่ม |
| `check(elapsed_sec: int)` | `list[CpegoMessage]` | ถ้าเพิ่งผ่าน milestone คืนข้อความ เช่น "You have studied for 15 mins, you got an egg!" |
| `reset()` | `None` | ล้างสถานะ |

### `CpegoPanel`

*class* · สืบทอดจาก `BaseWidget` · `ui/focus/cpego_panel.py`

กล่องแชทด้านขวา (desktop) / panel เปิดจากปุ่ม NOTI (mobile)

**สร้าง:** `CpegoPanel()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `messages` | `list[CpegoMessage]` | สร้างใน `__init__` = `[]` | ข้อความทั้งหมด |
| `unread_count` | `int` | สร้างใน `__init__` = `0` | ยังไม่อ่าน (โชว์บนปุ่ม NOTI) |
| `is_open` | `bool` | สร้างใน `__init__` = `True` | เปิดอยู่ไหม |
| `list_view` | `ft.ListView \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `add(message: CpegoMessage)` | `None` | เพิ่มข้อความ scroll ลงล่างสุด |
| `toggle()` | `None` | เปิด/ปิด ถ้าเปิดให้ unread_count = 0 |

### `FocusView`

*class* · สืบทอดจาก `BaseView` · `ui/focus/focus_view.py`

หน้า ④ ฟักไข่: นาฬิกา + ไข่ + แชท + ปุ่ม STOP

**สร้าง:** `FocusView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/focus"` |  |
| `session` | `SessionDTO \| None` | สร้างใน `__init__` = `None` | session ที่กำลังอ่าน (params["session_id"]) |
| `timer` | `StopwatchTimer \| None` | สร้างใน `__init__` = `None` |  |
| `time_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความ 67:07 |
| `egg_view` | `EggView \| None` | สร้างใน `__init__` = `None` |  |
| `bot` | `CpegoBot \| None` | สร้างใน `__init__` = `None` |  |
| `chat` | `CpegoPanel \| None` | สร้างใน `__init__` = `None` |  |
| `confirm` | `ConfirmDialog \| None` | สร้างใน `__init__` = `None` | Are you sure to stop? |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | เริ่ม timer + ส่ง greeting |
| `on_leave()` | `None` | หยุด timer |
| `on_tick(elapsed_sec: int)` | `None` | อัปเดตเวลา, bot.check, egg_view.set_tier |
| `ask_stop()` | `None` | เปิด ConfirmDialog |
| `confirm_stop()` | `None` | ctx.focus.stop แล้วไป /summary หรือ /report ถ้า FAILED |

<a id="p7"></a>

## P7 · Summary + Session Report

หน้า ⑤ Summary · รายงานหลังอ่านจบ · 6 class · 5 ไฟล์

### `SummaryService`

*class* · `app/services/summary_service.py`

ข้อมูลหน้า Summary หลังหยุดอ่าน

**สร้าง:** `SummaryService(database)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `database` | `Database` | ต้องส่งตอนสร้าง | database |
| `factory` | `EggFactory` | สร้างใน `__init__` = `EggFactory()` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `get_summary(session_id: int)` | `SummaryDTO` | ถ้า session ไม่ใช่ READY_TO_HATCH raise InvalidStateError |

### `AnalyticsService`

*class* · `app/services/analytics_service.py`

รายงานผล · P7 เขียน session_report, P9 เขียน history

**สร้าง:** `AnalyticsService(database)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `database` | `Database` | ต้องส่งตอนสร้าง | database |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `session_report(session_id: int)` | `SessionReport` | [P7] รายงานของรอบเดียว |
| `history(user_id: int)` | `History` | [P9] ทุกรอบ + สถิติรวม |
| `week_key(dt: datetime)` *staticmethod* | `str` | [P9] "2026-W39" (ISO week) |

### `EggChoiceCard`

*class* · สืบทอดจาก `BaseWidget` · `ui/summary/egg_choice_list.py`

การ์ดไข่หนึ่งระดับใน Choose an egg ถ้าล็อกให้เป็นสีเทากดไม่ได้

**สร้าง:** `EggChoiceCard(info, locked, on_select, selected=False)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `info` | `TierInfo` | ต้องส่งตอนสร้าง | ข้อมูลไข่ |
| `locked` | `bool` | ต้องส่งตอนสร้าง | ยังไม่ปลดล็อก |
| `on_select` | `Callable[[EggTier], None]` | ต้องส่งตอนสร้าง | กดเลือก |
| `selected` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `False` | ถูกเลือกอยู่ |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างการ์ด |

### `EggChoiceList`

*class* · สืบทอดจาก `BaseWidget` · `ui/summary/egg_choice_list.py`

รายการไข่ให้เลือก scroll ได้

**สร้าง:** `EggChoiceList(tiers, unlocked, on_select)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tiers` | `list[TierInfo]` | ต้องส่งตอนสร้าง | ทุกระดับ |
| `unlocked` | `list[EggTier]` | ต้องส่งตอนสร้าง | ระดับที่เลือกได้ |
| `on_select` | `Callable[[EggTier], None]` | ต้องส่งตอนสร้าง | ส่งต่อให้ SummaryView |
| `cards` | `list[EggChoiceCard]` | สร้างใน `__init__` = `[]` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |

### `SummaryView`

*class* · สืบทอดจาก `BaseView` · `ui/summary/summary_view.py`

หน้า ⑤ Summary: Total time, You can unlock ..., View Index, Choose an egg

**สร้าง:** `SummaryView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/summary"` |  |
| `summary` | `SummaryDTO \| None` | สร้างใน `__init__` = `None` |  |
| `choices` | `EggChoiceList \| None` | สร้างใน `__init__` = `None` |  |
| `selected_tier` | `EggTier \| None` | สร้างใน `__init__` = `None` | ไข่ที่กดเลือก |
| `confirm` | `ConfirmDialog \| None` | สร้างใน `__init__` = `None` | Are you sure to choose ...? |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | โหลด get_summary |
| `choose(tier: EggTier)` | `None` | เก็บ selected_tier แล้วเปิด confirm |
| `confirm_choose()` | `None` | ไป /hatch พร้อม session_id, tier |
| `view_index()` | `None` | ไป /dex |

### `ReportView`

*class* · สืบทอดจาก `BaseView` · `ui/report/report_view.py`

หน้า Analytics Report ของรอบเดียว: สำเร็จ/ไม่สำเร็จ, เวลา, สัตว์ที่ได้, ปุ่ม Return to lobby

**สร้าง:** `ReportView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/report"` |  |
| `report` | `SessionReport \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | โหลด session_report |
| `return_to_lobby()` | `None` | ไป /lobby |

<a id="p8"></a>

## P8 · Hatch / Gacha

หน้า ⑥ Egg pulling · 5 class · 5 ไฟล์

> มี method ที่ต้องเขียนในไฟล์ของคนอื่นด้วย: `OwnedPet` (app/models/owned_pet.py) ดู method ที่ขึ้นต้นด้วย **[P8]**

### `GachaMachine`

*class* · `app/domain/gacha.py`

ตัวสุ่ม ใส่ seed ได้เพื่อให้เทสต์ได้ผลเดิมทุกครั้ง

**สร้าง:** `GachaMachine(seed=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `seed` | `int \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | None = สุ่มจริง |
| `rng` | `random.Random` | สร้างใน `__init__` = `random.Random(seed)` | ตัวสุ่ม |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `pick_rarity(weights: dict[Rarity, int])` | `Rarity` | สุ่มตามน้ำหนัก (ข้าม weight 0) |
| `pick_species(pool: list[Species], rarity: Rarity)` | `Species` | สุ่มจาก pool ที่ rarity ตรง ถ้าไม่มีให้ลด rarity ลงทีละขั้น |

### `PetLevelPolicy`

*class* · `app/domain/pet_policy.py`

กติกา level และขนาด

**สร้าง:** `PetLevelPolicy()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `SCALE_STEP` | `float` | ค่าคงที่ของ class `= 0.15` | ใหญ่ขึ้นต่อ level |
| `MAX_SCALE` | `float` | ค่าคงที่ของ class `= 2.0` | ใหญ่สุด |
| `MAX_LEVEL` | `int` | ค่าคงที่ของ class `= 99` | level สูงสุด |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `next_level(level: int)` | `int` | level + 1 ไม่เกิน MAX_LEVEL |
| `scale_for(level: int)` | `float` | min(1 + (level − 1) × SCALE_STEP, MAX_SCALE) |

### `HatchService`

*class* · `app/services/hatch_service.py`

ฟักไข่: เช็ก session → สุ่ม → เพิ่มตัวใหม่หรือ level up → mark_hatched

**สร้าง:** `HatchService(database)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `database` | `Database` | ต้องส่งตอนสร้าง | database |
| `factory` | `EggFactory` | สร้างใน `__init__` = `EggFactory()` |  |
| `gacha` | `GachaMachine` | สร้างใน `__init__` = `GachaMachine()` |  |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `hatch(session_id: int, tier: EggTier)` | `HatchResult` | ถ้า session ไม่ READY หรือ tier ยังไม่ปลดล็อก raise InvalidStateError |

### `HatchAnimation`

*class* · สืบทอดจาก `BaseWidget` · `ui/hatch/hatch_animation.py`

animation 4 ขั้น: ไข่สั่น → แตก → TADA (แสง + SFX) → Congrats

**สร้าง:** `HatchAnimation(egg_image_path, pet, stage_ms=900)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `egg_image_path` | `str` | ต้องส่งตอนสร้าง | รูปไข่ที่เลือก |
| `pet` | `PetDTO` | ต้องส่งตอนสร้าง | สัตว์ที่ได้ |
| `STAGES` | `tuple[str, ...]` | ค่าคงที่ของ class `= ("shake", "crack", "reveal", "congrats")` | ลำดับขั้น |
| `stage_ms` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `900` | เวลาต่อขั้น |
| `current_stage` | `int` | สร้างใน `__init__` = `0` | ขั้นที่เล่นอยู่ |
| `stack` | `ft.Stack \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `play(page: ft.Page, on_done: Callable[[], None])` | `None` | เล่นทีละขั้นด้วย page.run_task แล้วเรียก on_done |
| `skip()` | `None` | กดข้ามไปขั้นสุดท้าย |

### `HatchView`

*class* · สืบทอดจาก `BaseView` · `ui/hatch/hatch_view.py`

หน้า ⑥ Egg pulling: เรียก hatch แล้วเล่น animation จบแล้วโชว์ Congrats! You got ... + ปุ่ม Return to lobby

**สร้าง:** `HatchView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/hatch"` |  |
| `result` | `HatchResult \| None` | สร้างใน `__init__` = `None` | ผลการฟัก |
| `animation` | `HatchAnimation \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | ctx.hatch.hatch(params["session_id"], params["tier"]) แล้ว play |
| `on_animation_done()` | `None` | โชว์ชื่อ + ข้อความตัวใหม่ / level up |
| `go_report()` | `None` | ไป /report |

<a id="p9"></a>

## P9 · CPE Dex + History

สมุดสะสม · ประวัติและสถิติ · 6 class · 6 ไฟล์

> มี method ที่ต้องเขียนในไฟล์ของคนอื่นด้วย: `AnalyticsService` (app/services/analytics_service.py) ดู method ที่ขึ้นต้นด้วย **[P9]**

### `DexService`

*class* · `app/services/dex_service.py`

ข้อมูล CPE Dex: สัตว์ทุกชนิด พร้อมบอกว่าปลดล็อกหรือยัง

**สร้าง:** `DexService(database)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `database` | `Database` | ต้องส่งตอนสร้าง | database |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `list_entries(user_id: int)` | `list[DexEntry]` | ทุกชนิด เรียง tier แล้ว rarity |
| `get_entry(user_id: int, species_id: int)` | `DexEntry` | หนึ่งชนิด + subjects |
| `completion(user_id: int)` | `float` | สัดส่วนที่ปลดล็อก 0.0 ถึง 1.0 |

### `DexCard`

*class* · สืบทอดจาก `BaseWidget` · `ui/dex/dex_card.py`

ช่องหนึ่งช่องใน grid ถ้ายังไม่ปลดล็อกเป็นเงาดำ ถ้าถูกเลือกมีกรอบ highlight

**สร้าง:** `DexCard(entry, on_select, selected=False)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `entry` | `DexEntry` | ต้องส่งตอนสร้าง |  |
| `on_select` | `Callable[[DexEntry], None]` | ต้องส่งตอนสร้าง |  |
| `selected` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `False` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `set_selected(selected: bool)` | `None` | เปลี่ยน highlight |

### `DexDetailPanel`

*class* · สืบทอดจาก `BaseWidget` · `ui/dex/dex_detail_panel.py`

panel ด้านขวา: รูปใหญ่, ชื่อ, tier, level, วิชาที่อ่าน

**สร้าง:** `DexDetailPanel(entry=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `entry` | `DexEntry \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ตัวที่เลือก |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `show(entry: DexEntry)` | `None` | เปลี่ยนตัวที่โชว์ |

### `DexView`

*class* · สืบทอดจาก `BaseView` · `ui/dex/dex_view.py`

หน้า CPE Dex: grid + scrollbar + detail + ปุ่มปิดกลับ lobby

**สร้าง:** `DexView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/dex"` |  |
| `entries` | `list[DexEntry]` | สร้างใน `__init__` = `[]` |  |
| `cards` | `list[DexCard]` | สร้างใน `__init__` = `[]` |  |
| `selected` | `DexEntry \| None` | สร้างใน `__init__` = `None` |  |
| `detail` | `DexDetailPanel \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | โหลด list_entries |
| `select(entry: DexEntry)` | `None` | เลือก + อัปเดต detail |
| `close()` | `None` | กลับ /lobby |

### `WeeklyChart`

*class* · สืบทอดจาก `BaseWidget` · `ui/report/weekly_chart.py`

กราฟแท่งเวลาอ่านรายสัปดาห์ (วาดด้วย Container ไม่ต้องใช้ library กราฟ)

**สร้าง:** `WeeklyChart(weekly_study_sec, max_bars=8, bar_height=160)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `weekly_study_sec` | `dict[str, int]` | ต้องส่งตอนสร้าง | จาก HistoryStats |
| `max_bars` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `8` | โชว์กี่สัปดาห์ล่าสุด |
| `bar_height` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `160` | ความสูงแท่งสูงสุด |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างกราฟ |

### `HistoryView`

*class* · สืบทอดจาก `BaseView` · `ui/report/history_view.py`

หน้าประวัติ: สถิติรวม + กราฟ + รายการทุกรอบ กดรายการไปดู ReportView

**สร้าง:** `HistoryView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/history"` |  |
| `history` | `History \| None` | สร้างใน `__init__` = `None` |  |
| `chart` | `WeeklyChart \| None` | สร้างใน `__init__` = `None` |  |

| method | คืนค่า | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | โหลด history |
| `render_row(report: SessionReport)` | `ft.Control` | หนึ่งแถว |
| `open_report(session_id: int)` | `None` | ไป /report |
