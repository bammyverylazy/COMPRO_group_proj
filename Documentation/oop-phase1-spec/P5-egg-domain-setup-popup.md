# P5 · Egg domain + Setup popup

Phase 1 · ไข่ 3 ระดับ, popup ใส่วิชา + Egg Rate · 8 class · 5 ไฟล์

> อ่าน [00-shared.md](00-shared.md) ก่อน (กติกาการตั้งชื่อ, ตัวแปร 4 แบบ, Enum, Error, DTO)

## สรุปงาน

- **ไฟล์ที่ต้องเขียน:** `app/domain/eggs.py`, `app/domain/egg_factory.py`, `app/services/tier_service.py`, `ui/lobby/egg_rate_panel.py`, `ui/lobby/setup_popup.py`
- **ต้องใช้ของ:** P2 (`Species`, `GameStore`), P3 (`BaseWidget`, `Popup`), P6 (`FocusSessionService.start`), P8 (`GachaMachine` ที่ `Egg.roll` ใช้)
- **คนที่ใช้ของเรา:** P4 เปิด `SetupPopup` · P6, P7, P8 ใช้ `EggFactory` / `TierService`
- **ส่งงาน:** branch `feat/egg-domain-setup-popup` → PR ให้เพื่อนรีวิว 1 คน

## Class ที่ต้องเขียน

### `Egg`

*abstract class* · `app/domain/eggs.py`

แม่ของไข่ทุกระดับ (abstraction + polymorphism)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.FRESHMAN` | ลูก override |
| `name_th` | `str` | ค่าคงที่ของ class `= ""` | ชื่อไทย |
| `image_path` | `str` | ค่าคงที่ของ class `= ""` | รูปไข่ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `required_minutes()` *abstract* | `int` | เวลาขั้นต่ำ |
| `rarity_weights()` *abstract* | `dict[Rarity, int]` | โอกาสแต่ละ rarity รวม 100 |
| `is_unlocked(duration_sec: int)` | `bool` | duration_sec ≥ required_minutes × 60 |
| `roll(pool: list[Species], gacha: GachaMachine)` | `Species` | สุ่ม rarity แล้วสุ่มสัตว์ |
| `to_tier_info()` | `TierInfo` | แปลงเป็น TierInfo |

### `FreshmanEgg`

*class* · สืบทอดจาก `Egg` · `app/domain/eggs.py`

ไข่รุ่นเรา 15 นาที

**สร้าง:** `FreshmanEgg()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.FRESHMAN` | ระดับของไข่นี้ |
| `name_th` | `str` | ค่าคงที่ของ class `= "ไข่รุ่นเรา"` | ชื่อไทย |
| `image_path` | `str` | ค่าคงที่ของ class `= "eggs/freshman.png"` | รูปไข่ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `required_minutes()` *เขียนให้แล้ว* | `int` | 15 |
| `rarity_weights()` *เขียนให้แล้ว* | `dict[Rarity, int]` | 70 / 25 / 5 / 0 |

### `SeniorEgg`

*class* · สืบทอดจาก `Egg` · `app/domain/eggs.py`

ไข่รุ่นพี่ 30 นาที

**สร้าง:** `SeniorEgg()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.SENIOR` | ระดับของไข่นี้ |
| `name_th` | `str` | ค่าคงที่ของ class `= "ไข่รุ่นพี่"` | ชื่อไทย |
| `image_path` | `str` | ค่าคงที่ของ class `= "eggs/senior.png"` | รูปไข่ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `required_minutes()` *เขียนให้แล้ว* | `int` | 30 |
| `rarity_weights()` *เขียนให้แล้ว* | `dict[Rarity, int]` | 40 / 40 / 17 / 3 |

### `ProfessorEgg`

*class* · สืบทอดจาก `Egg` · `app/domain/eggs.py`

ไข่อาจารย์ 60 นาที

**สร้าง:** `ProfessorEgg()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier` | ค่าคงที่ของ class `= EggTier.PROFESSOR` | ระดับของไข่นี้ |
| `name_th` | `str` | ค่าคงที่ของ class `= "ไข่อาจารย์"` | ชื่อไทย |
| `image_path` | `str` | ค่าคงที่ของ class `= "eggs/professor.png"` | รูปไข่ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `required_minutes()` *เขียนให้แล้ว* | `int` | 60 |
| `rarity_weights()` *เขียนให้แล้ว* | `dict[Rarity, int]` | 10 / 40 / 35 / 15 |

### `EggFactory`

*class* · `app/domain/egg_factory.py`

สร้าง Egg จาก EggTier และบอกว่าเวลาเท่านี้ปลดล็อกไข่อะไร

**สร้าง:** `EggFactory()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_registry` | `dict[EggTier, type[Egg]]` | สร้างใน `__init__` = `{EggTier.FRESHMAN: FreshmanEgg, EggTier.SENIOR: SeniorEgg, EggTier.PROFESSOR: ProfessorEgg}` | tier → class |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `create(tier: EggTier)` | `Egg` | สร้างไข่ |
| `all()` | `list[Egg]` | ทุกระดับ ต่ำไปสูง |
| `unlocked_for(duration_sec: int)` | `list[Egg]` | ไข่ที่ปลดล็อก |
| `best_for(duration_sec: int)` | `Egg \| None` | ไข่สูงสุดที่ปลดล็อก |

### `TierService`

*class* · `app/services/tier_service.py`

ข้อมูลไข่ทุกระดับให้หน้าจอ

**สร้าง:** `TierService()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `factory` | `EggFactory` | สร้างใน `__init__` = `EggFactory()` | สร้างไข่ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `list_tiers()` | `list[TierInfo]` | ทุกระดับ ต่ำไปสูง |

### `EggRatePanel`

*class* · สืบทอดจาก `BaseWidget` · `ui/lobby/egg_rate_panel.py`

ตาราง Egg Rate: แต่ละระดับใช้กี่นาที โอกาสแต่ละ rarity

**สร้าง:** `EggRatePanel(tiers)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tiers` | `list[TierInfo]` | ต้องส่งตอนสร้าง | ข้อมูลไข่ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `render_tier(info: TierInfo)` | `ft.Control` | หนึ่งแถว |

### `SetupPopup`

*class* · สืบทอดจาก `BaseWidget` · `ui/lobby/setup_popup.py`

popup หลังกด START FOCUS: ช่องใส่ชื่อวิชา, Egg Rate, ปุ่ม START / BACK

**สร้าง:** `SetupPopup(ctx, on_started, on_back)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `ctx` | `AppContext` | ต้องส่งตอนสร้าง | ของกลาง |
| `on_started` | `Callable[[SessionDTO], None]` | ต้องส่งตอนสร้าง | เรียกหลังเริ่ม session สำเร็จ |
| `on_back` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กด BACK |
| `subject_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` | ช่องชื่อวิชา |
| `error_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความเตือนสีแดง |
| `egg_rate` | `EggRatePanel \| None` | สร้างใน `__init__` = `None` | - |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `subject` *property* | `str` | ชื่อวิชา ตัดช่องว่างแล้ว |
| `start()` | `None` | ctx.focus.start(subject) แล้ว on_started · ถ้า ValidationError โชว์ error_text |
