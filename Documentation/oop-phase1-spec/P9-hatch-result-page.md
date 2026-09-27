# P9 · Hatch/Result page

Phase 1 · หน้า ④ animation ฟักไข่ + สรุปผล · 4 class · 4 ไฟล์

> อ่าน [00-shared.md](00-shared.md) ก่อน (กติกาการตั้งชื่อ, ตัวแปร 4 แบบ, Enum, Error, DTO)

## สรุปงาน

- **ไฟล์ที่ต้องเขียน:** `app/services/result_service.py`, `ui/hatch/hatch_animation.py`, `ui/hatch/result_card.py`, `ui/hatch/hatch_result_view.py`
- **ต้องใช้ของ:** P3 (`BaseView`, `BaseWidget`), P8 (`HatchService`, `PetLevelPolicy`), P1 (`SoundManager` เสียง TADA)
- **คนที่ใช้ของเรา:** ปลายทางของทุกรอบการเล่น
- **ส่งงาน:** branch `feat/hatch-result-page` → PR ให้เพื่อนรีวิว 1 คน

## Class ที่ต้องเขียน

### `ResultService`

*class* · `app/services/result_service.py`

สร้างข้อมูลสรุปผลของรอบที่อ่าน ทั้งสำเร็จและไม่สำเร็จ

**สร้าง:** `ResultService(store, settings)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง (GameStore) |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | min_success_minutes |
| `policy` | `PetLevelPolicy` | สร้างใน `__init__` = `PetLevelPolicy()` | กติกา level/ขนาด |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `get_report(session_id: int)` | `SessionReport` | ถ้ายัง RUNNING หรือ READY_TO_HATCH raise InvalidStateError |

### `HatchAnimation`

*class* · สืบทอดจาก `BaseWidget` · `ui/hatch/hatch_animation.py`

animation 3 ขั้น: ไข่สั่น → แตก → TADA (แสง + SFX)

**สร้าง:** `HatchAnimation(egg_image_path, pet, stage_ms=900)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `egg_image_path` | `str` | ต้องส่งตอนสร้าง | รูปไข่ที่เลือก |
| `pet` | `PetDTO` | ต้องส่งตอนสร้าง | สัตว์ที่ได้ |
| `STAGES` | `tuple[str, ...]` | ค่าคงที่ของ class `= ("shake", "crack", "reveal")` | ลำดับขั้น |
| `stage_ms` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `900` | เวลาต่อขั้น |
| `current_stage` | `int` | สร้างใน `__init__` = `0` | ขั้นที่เล่นอยู่ |
| `stack` | `ft.Stack \| None` | สร้างใน `__init__` = `None` | ft.Stack ที่วางของ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `play(page: ft.Page, on_done: Callable[[], None])` | `None` | เล่นทีละขั้น จบแล้วเรียก on_done |
| `skip()` | `None` | ข้ามไปขั้นสุดท้าย |

### `ResultCard`

*class* · สืบทอดจาก `BaseWidget` · `ui/hatch/result_card.py`

การ์ดสรุปผล: สำเร็จ = Congrats! You got ... / ไม่สำเร็จ = ไข่ยังไม่ฟัก + ต้องอ่านอีกกี่นาที

**สร้าง:** `ResultCard(report, on_return)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `report` | `SessionReport` | ต้องส่งตอนสร้าง | ข้อมูลสรุป |
| `on_return` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กด RETURN TO LOBBY |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | เลือก build_success หรือ build_failed ตาม report.is_success |
| `build_success()` | `ft.Control` | ชื่อสัตว์, rarity, ตัวใหม่/level up, วิชา, เวลา |
| `build_failed()` | `ft.Control` | วิชา, เวลาที่อ่าน, ต้องอ่านอีกกี่นาที |

### `HatchResultView`

*class* · สืบทอดจาก `BaseView` · `ui/hatch/hatch_result_view.py`

หน้า ④ Hatch/Result: มี tier ใน params = ฟักไข่แล้วโชว์ผล · ไม่มี tier = โชว์ผลไม่สำเร็จเลย

**สร้าง:** `HatchResultView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/hatch"` | path ของหน้า |
| `hatch_result` | `HatchResult \| None` | สร้างใน `__init__` = `None` | ผลการฟัก |
| `report` | `SessionReport \| None` | สร้างใน `__init__` = `None` | ข้อมูลสรุป |
| `animation` | `HatchAnimation \| None` | สร้างใน `__init__` = `None` | animation ฟักไข่ |
| `card` | `ResultCard \| None` | สร้างใน `__init__` = `None` | การ์ดสรุปผล |
| `body` | `ft.Container \| None` | สร้างใน `__init__` = `None` | กล่องที่สลับ animation ↔ การ์ด |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | มี tier → ctx.hatch.hatch แล้ว play · ไม่มี → show_result |
| `show_result()` | `None` | ctx.results.get_report แล้วโชว์ ResultCard |
| `return_to_lobby()` | `None` | ไป /lobby |
