# P8 · Hatch logic

Phase 1 · สุ่มสัตว์, level, HatchService · 3 class · 3 ไฟล์

> อ่าน [00-shared.md](00-shared.md) ก่อน (กติกาการตั้งชื่อ, ตัวแปร 4 แบบ, Enum, Error, DTO)

## สรุปงาน

- **ไฟล์ที่ต้องเขียน:** `app/domain/gacha.py`, `app/domain/pet_policy.py`, `app/services/hatch_service.py`
- **method ในไฟล์ของคนอื่นที่ต้องเขียนด้วย:** `OwnedPet` ใน `app/domain/owned_pet.py`
- **ต้องใช้ของ:** P2 (`GameStore`, `OwnedPet`, `Species`), P5 (`Egg`, `EggFactory`), P6 (`StudySession.can_hatch`, `mark_hatched`)
- **คนที่ใช้ของเรา:** P4 ใช้ `PetLevelPolicy` คำนวณขนาด · P9 เรียก `HatchService.hatch()`
- **ส่งงาน:** branch `feat/hatch-logic` → PR ให้เพื่อนรีวิว 1 คน

## Class ที่ต้องเขียน

### `GachaMachine`

*class* · `app/domain/gacha.py`

ตัวสุ่ม ใส่ seed ได้เพื่อให้เทสต์ได้ผลเดิม

**สร้าง:** `GachaMachine(seed=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `seed` | `int \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | None = สุ่มจริง |
| `rng` | `random.Random` | สร้างใน `__init__` = `random.Random(seed)` | ตัวสุ่ม |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `pick_rarity(weights: dict[Rarity, int])` | `Rarity` | สุ่มตามน้ำหนัก (ข้าม weight 0) |
| `pick_species(pool: list[Species], rarity: Rarity)` | `Species` | สุ่มจาก pool ที่ rarity ตรง ถ้าไม่มีลด rarity ลงทีละขั้น |

### `PetLevelPolicy`

*class* · `app/domain/pet_policy.py`

กติกา level และขนาด

**สร้าง:** `PetLevelPolicy()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `SCALE_STEP` | `float` | ค่าคงที่ของ class `= 0.15` | ใหญ่ขึ้นต่อ level |
| `MAX_SCALE` | `float` | ค่าคงที่ของ class `= 2.0` | ใหญ่สุด |
| `MAX_LEVEL` | `int` | ค่าคงที่ของ class `= 99` | level สูงสุด |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `next_level(level: int)` | `int` | level + 1 ไม่เกิน MAX_LEVEL |
| `scale_for(level: int)` | `float` | min(1 + (level − 1) × SCALE_STEP, MAX_SCALE) |

### `HatchService`

*class* · `app/services/hatch_service.py`

ฟักไข่: เช็ก session → สุ่ม → เพิ่มตัวใหม่หรือ level up → mark_hatched

**สร้าง:** `HatchService(store)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง (GameStore) |
| `factory` | `EggFactory` | สร้างใน `__init__` = `EggFactory()` | สร้างไข่ |
| `gacha` | `GachaMachine` | สร้างใน `__init__` = `GachaMachine()` | ตัวสุ่ม |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` | กติกา level/ขนาด |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `hatch(session_id: int, tier: EggTier)` | `HatchResult` | session ไม่ READY หรือ tier ยังไม่ปลดล็อก raise InvalidStateError |

## Method ที่ต้องเขียนในไฟล์ของคนอื่น

### `OwnedPet`

*class* · `app/domain/owned_pet.py`

สัตว์ที่ผู้เล่นมี หนึ่งชนิดมีได้ตัวเดียว ได้ซ้ำ = level up · P2 สร้างตัวแปร, P8 เขียน method

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `level_up(policy: PetLevelPolicy)` | `None` | times_hatched +1 และ level ตาม policy |
| `scale(policy: PetLevelPolicy)` | `float` | ขนาดตาม level |
| `to_dto(species: Species, policy: PetLevelPolicy)` | `PetDTO` | แปลงเป็น PetDTO |
