# P2 · Core data (in-memory)

Phase 1 · Settings, Clock, Species, ที่เก็บข้อมูลใน memory · 13 class · 9 ไฟล์

> อ่าน [00-shared.md](00-shared.md) ก่อน (กติกาการตั้งชื่อ, ตัวแปร 4 แบบ, Enum, Error, DTO)

## สรุปงาน

- **ไฟล์ที่ต้องเขียน:** `app/config.py`, `app/core/clock.py`, `app/domain/species.py`, `app/domain/study_session.py`, `app/domain/owned_pet.py`, `app/data/species_loader.py`, `app/data/repositories.py`, `app/data/memory_repositories.py`, `app/data/game_store.py`
- **ต้องใช้ของ:** ไม่มี · ต้องเสร็จก่อน เพราะทุก service ใช้ `GameStore`, `Clock`, DTO
- **คนที่ใช้ของเรา:** ทุกคน
- **ส่งงาน:** branch `feat/core-data-in-memory` → PR ให้เพื่อนรีวิว 1 คน

## Class ที่ต้องเขียน

### `Settings`

*dataclass* · `app/config.py`

ค่าตั้งค่ารวมไว้ที่เดียว ห้าม hard-code ตัวเลขพวกนี้ในไฟล์อื่น

**สร้าง:** `Settings()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `min_success_minutes` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `15` | อ่านขั้นต่ำกี่นาทีถึงได้ไข่ |
| `demo_speed` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1.0` | เร่งเวลาตอนเดโม 60.0 = 1 วินาทีจริงนับเป็น 1 นาที |
| `species_seed_path` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"seed/species.json"` | ไฟล์รายชื่อสัตว์ |
| `window_width` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1280` | ความกว้างหน้าต่างเริ่มต้น |
| `window_height` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `800` | ความสูงหน้าต่างเริ่มต้น |

### `Clock`

*class* · `app/core/clock.py`

นาฬิกากลางของเกม ทุกคนขอเวลาจากที่นี่ รองรับโหมดเร่งเวลาตอนเดโม

**สร้าง:** `Clock(speed=1.0)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `speed` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1.0` | มาจาก Settings.demo_speed |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `now()` | `datetime` | เวลาจริงตอนนี้ (UTC) |
| `elapsed_sec(started_at: datetime, until: datetime \| None = None)` | `int` | วินาทีเกมตั้งแต่ started_at ถึง until (ไม่ส่ง = ตอนนี้) คูณ speed แล้วปัดลง |

### `Species`

*dataclass (แก้ค่าไม่ได้)* · `app/domain/species.py`

สัตว์หนึ่งชนิด โหลดจาก species.json

**สร้าง:** `Species(code=..., name=..., tier=..., rarity=..., sprite_path=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `code` | `str` | ต้องส่งตอนสร้าง | รหัสไม่ซ้ำ |
| `name` | `str` | ต้องส่งตอนสร้าง | ชื่อ |
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ระดับไข่ |
| `rarity` | `Rarity` | ต้องส่งตอนสร้าง | ความหายาก |
| `sprite_path` | `str` | ต้องส่งตอนสร้าง | path รูป |
| `description` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `""` | คำอธิบาย |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `to_dto()` | `SpeciesDTO` | แปลงเป็น SpeciesDTO |

### `StudySession`

*class* · `app/domain/study_session.py`

การอ่านหนึ่งรอบ · P2 สร้างตัวแปร, P6 เขียน method (encapsulation: เปลี่ยน status ผ่าน method เท่านั้น)

**สร้าง:** `StudySession(id, subject, started_at)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | session_id |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `status` | `SessionStatus` | สร้างใน `__init__` = `SessionStatus.RUNNING` | สถานะ |
| `ended_at` | `datetime \| None` | สร้างใน `__init__` = `None` | เวลาหยุด |
| `duration_sec` | `int` | สร้างใน `__init__` = `0` | เวลาที่อ่าน คำนวณตอน stop |
| `chosen_tier` | `EggTier \| None` | สร้างใน `__init__` = `None` | ไข่ที่เลือก |
| `species_code` | `str \| None` | สร้างใน `__init__` = `None` | สัตว์ที่ได้ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `stop(ended_at: datetime, duration_sec: int, min_success_sec: int)` | `SessionStatus` | บันทึกเวลา แล้วเปลี่ยนเป็น FAILED หรือ READY_TO_HATCH · ถ้าไม่ได้ RUNNING ให้ raise InvalidStateError |
| `can_hatch()` | `bool` | True ถ้า READY_TO_HATCH |
| `mark_hatched(tier: EggTier, species_code: str)` | `None` | บันทึกไข่ + สัตว์ เปลี่ยนเป็น HATCHED |
| `is_success()` | `bool` | True ถ้า HATCHED |
| `to_dto()` | `SessionDTO` | แปลงเป็น SessionDTO |

### `OwnedPet`

*class* · `app/domain/owned_pet.py`

สัตว์ที่ผู้เล่นมี หนึ่งชนิดมีได้ตัวเดียว ได้ซ้ำ = level up · P2 สร้างตัวแปร, P8 เขียน method

**สร้าง:** `OwnedPet(species_code, hatched_at, level=1, times_hatched=1)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `species_code` | `str` | ต้องส่งตอนสร้าง | ชนิด |
| `hatched_at` | `datetime` | ต้องส่งตอนสร้าง | ได้ครั้งแรกเมื่อไหร่ |
| `level` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1` | level |
| `times_hatched` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1` | ฟักได้กี่ครั้ง |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `level_up(policy: PetLevelPolicy)` | `None` | times_hatched +1 และ level ตาม policy |
| `scale(policy: PetLevelPolicy)` | `float` | ขนาดตาม level |
| `to_dto(species: Species, policy: PetLevelPolicy)` | `PetDTO` | แปลงเป็น PetDTO |

### `SpeciesLoader`

*class* · `app/data/species_loader.py`

อ่าน seed/species.json แล้วสร้างเป็น list ของ Species

**สร้าง:** `SpeciesLoader(path)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `path` | `Path` | ต้องส่งตอนสร้าง | ไฟล์ json |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `load()` | `list[Species]` | อ่านไฟล์ แปลง tier/rarity เป็น Enum ถ้าไฟล์ผิดรูปแบบ raise AppError |

### `SpeciesRepository`

*abstract class* · `app/data/repositories.py`

ที่เก็บสัตว์ทุกชนิด (abstract) Phase 2 สร้างลูกแบบ database ได้โดยไม่ต้องแก้ service

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `list_all()` *abstract* | `list[Species]` | ทุกชนิด |
| `list_by_tier(tier: EggTier)` *abstract* | `list[Species]` | pool สำหรับสุ่มของไข่ระดับนี้ |
| `get(code: str)` *abstract* | `Species` | หาจาก code ไม่เจอ raise NotFoundError |

### `SessionRepository`

*abstract class* · `app/data/repositories.py`

ที่เก็บการอ่านแต่ละรอบ (abstract)

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `create(subject: str, started_at: datetime)` *abstract* | `StudySession` | สร้าง session ใหม่ให้ id อัตโนมัติ |
| `get(session_id: int)` *abstract* | `StudySession` | ไม่เจอ raise NotFoundError |
| `get_running()` *abstract* | `StudySession \| None` | session ที่ RUNNING อยู่ (มีได้อันเดียว) |

### `PetRepository`

*abstract class* · `app/data/repositories.py`

ที่เก็บสัตว์ที่ผู้เล่นมี (abstract)

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `find(species_code: str)` *abstract* | `OwnedPet \| None` | มีตัวนี้หรือยัง |
| `add(pet: OwnedPet)` *abstract* | `None` | เพิ่มตัวใหม่ |
| `list_all()` *abstract* | `list[OwnedPet]` | ทุกตัว เรียงตามเวลาที่ได้ |

### `InMemorySpeciesRepository`

*class* · สืบทอดจาก `SpeciesRepository` · `app/data/memory_repositories.py`

เก็บสัตว์ใน dict (Phase 1)

**สร้าง:** `InMemorySpeciesRepository()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_species` | `dict[str, Species]` | สร้างใน `__init__` = `{}` | code → Species |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `add_many(species: list[Species])` | `None` | ใส่สัตว์จาก SpeciesLoader |
| `list_all()` | `list[Species]` | ทำตาม class แม่ |
| `list_by_tier(tier: EggTier)` | `list[Species]` | ทำตาม class แม่ |
| `get(code: str)` | `Species` | ทำตาม class แม่ |

### `InMemorySessionRepository`

*class* · สืบทอดจาก `SessionRepository` · `app/data/memory_repositories.py`

เก็บ session ใน dict (Phase 1)

**สร้าง:** `InMemorySessionRepository()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_sessions` | `dict[int, StudySession]` | สร้างใน `__init__` = `{}` | id → StudySession |
| `_next_id` | `int` | สร้างใน `__init__` = `1` | id ถัดไป |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `create(subject: str, started_at: datetime)` | `StudySession` | ทำตาม class แม่ |
| `get(session_id: int)` | `StudySession` | ทำตาม class แม่ |
| `get_running()` | `StudySession \| None` | ทำตาม class แม่ |

### `InMemoryPetRepository`

*class* · สืบทอดจาก `PetRepository` · `app/data/memory_repositories.py`

เก็บสัตว์ที่มีใน dict (Phase 1)

**สร้าง:** `InMemoryPetRepository()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_pets` | `dict[str, OwnedPet]` | สร้างใน `__init__` = `{}` | species_code → OwnedPet |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `find(species_code: str)` | `OwnedPet \| None` | ทำตาม class แม่ |
| `add(pet: OwnedPet)` | `None` | ทำตาม class แม่ |
| `list_all()` | `list[OwnedPet]` | ทำตาม class แม่ |

### `GameStore`

*class* · `app/data/game_store.py`

รวมที่เก็บข้อมูลทั้ง 3 อย่างไว้ที่เดียว service ทุกตัวรับ GameStore · Phase 2 เพิ่ม create_database() แทน

**สร้าง:** `GameStore(species, sessions, pets)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `species` | `SpeciesRepository` | ต้องส่งตอนสร้าง | สัตว์ทุกชนิด |
| `sessions` | `SessionRepository` | ต้องส่งตอนสร้าง | การอ่าน |
| `pets` | `PetRepository` | ต้องส่งตอนสร้าง | สัตว์ที่มี |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `create_in_memory(settings: Settings)` *classmethod* | `GameStore` | สร้าง InMemory repo ทั้ง 3 แล้วโหลดสัตว์จาก SpeciesLoader |
