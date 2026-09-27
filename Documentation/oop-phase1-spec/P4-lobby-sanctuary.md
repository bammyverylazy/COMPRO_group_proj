# P4 · Lobby + Sanctuary

Phase 1 · หน้า ② Lobby ห้องภาค สัตว์เดินไปมา · 4 class · 4 ไฟล์

> อ่าน [00-shared.md](00-shared.md) ก่อน (กติกาการตั้งชื่อ, ตัวแปร 4 แบบ, Enum, Error, DTO)

## สรุปงาน

- **ไฟล์ที่ต้องเขียน:** `app/services/sanctuary_service.py`, `ui/lobby/pet_sprite.py`, `ui/lobby/sanctuary_scene.py`, `ui/lobby/lobby_view.py`
- **ต้องใช้ของ:** P2 (`GameStore`), P3 (`BaseView`), P1 (`HowToPopup`), P5 (`SetupPopup`), P8 (`PetLevelPolicy`, `OwnedPet.to_dto`)
- **คนที่ใช้ของเรา:** หน้า Lobby เป็นหน้าที่ทุกหน้ากลับมา
- **ส่งงาน:** branch `feat/lobby-sanctuary` → PR ให้เพื่อนรีวิว 1 คน

## Class ที่ต้องเขียน

### `SanctuaryService`

*class* · `app/services/sanctuary_service.py`

ดึงสัตว์ทั้งหมดไปโชว์ในห้องภาค

**สร้าง:** `SanctuaryService(store)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูล |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` | คำนวณ scale |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `list_pets()` | `list[PetDTO]` | ทุกตัว + level + scale |

### `PetSprite`

*class* · `ui/lobby/pet_sprite.py`

สัตว์หนึ่งตัวที่เดินในห้อง เดินไปจุดสุ่ม หยุดพัก แล้วสุ่มใหม่

**สร้าง:** `PetSprite(pet, x, y, speed=40.0)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `pet` | `PetDTO` | ต้องส่งตอนสร้าง | ข้อมูลสัตว์ |
| `x` | `float` | ต้องส่งตอนสร้าง | ตำแหน่งแนวนอน |
| `y` | `float` | ต้องส่งตอนสร้าง | ตำแหน่งแนวตั้ง |
| `BASE_SIZE` | `int` | ค่าคงที่ของ class `= 64` | ขนาดตอน level 1 |
| `speed` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `40.0` | px ต่อวินาที |
| `target_x` | `float` | สร้างใน `__init__` = `x` | จุดที่กำลังเดินไป |
| `target_y` | `float` | สร้างใน `__init__` = `y` | จุดที่กำลังเดินไป (แนวตั้ง) |
| `rest_sec` | `float` | สร้างใน `__init__` = `0.0` | เหลือเวลาพัก |
| `facing_left` | `bool` | สร้างใน `__init__` = `False` | หันซ้ายไหม |
| `image` | `ft.Image \| None` | สร้างใน `__init__` = `None` | รูป |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `size` *property* | `float` | BASE_SIZE × pet.scale |
| `build()` | `ft.Control` | สร้าง ft.Image |
| `choose_target(width: float, height: float)` | `None` | สุ่มจุดใหม่ |
| `update(dt: float, width: float, height: float)` | `None` | ขยับตาม speed ถึงแล้วพัก 1-3 วิ |

### `SanctuaryScene`

*class* · สืบทอดจาก `BaseWidget` · `ui/lobby/sanctuary_scene.py`

ฉากห้องภาค: พื้นหลัง + สัตว์ทุกตัว อัปเดตทุก tick

**สร้าง:** `SanctuaryScene(width, height, fps=20)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `width` | `float` | ต้องส่งตอนสร้าง | กว้าง |
| `height` | `float` | ต้องส่งตอนสร้าง | สูง |
| `fps` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `20` | อัปเดตต่อวินาที |
| `sprites` | `list[PetSprite]` | สร้างใน `__init__` = `[]` | สัตว์ในห้อง |
| `running` | `bool` | สร้างใน `__init__` = `False` | loop ทำงานไหม |
| `stack` | `ft.Stack \| None` | สร้างใน `__init__` = `None` | Stack ที่วางสัตว์ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `load(pets: list[PetDTO])` | `None` | สร้าง PetSprite วางตำแหน่งสุ่ม |
| `start(page: ft.Page)` | `None` | เริ่ม loop ด้วย page.run_task |
| `stop()` | `None` | หยุด |
| `tick(dt: float)` | `None` | update ทุก sprite แล้ว refresh |

### `LobbyView`

*class* · สืบทอดจาก `BaseView` · `ui/lobby/lobby_view.py`

หน้า ② Lobby: ห้องภาค + ปุ่ม HOW TO + START FOCUS (ห้องว่างให้โชว์ข้อความชวนเริ่มอ่าน)

**สร้าง:** `LobbyView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/lobby"` | path ของหน้า |
| `scene` | `SanctuaryScene \| None` | สร้างใน `__init__` = `None` | ฉาก |
| `howto` | `HowToPopup \| None` | สร้างใน `__init__` = `None` | P1 |
| `setup` | `SetupPopup \| None` | สร้างใน `__init__` = `None` | P5 |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | list_pets แล้ว scene.start |
| `on_leave()` | `None` | scene.stop |
| `open_howto()` | `None` | เปิด HowToPopup |
| `start_focus()` | `None` | เปิด SetupPopup |
| `on_session_started(session: SessionDTO)` | `None` | ไป /focus พร้อม session_id |
