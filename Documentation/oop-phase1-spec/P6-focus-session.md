# P6 · Focus session

Phase 1 · หน้า ③ Focus นาฬิกานับขึ้น + STOP · 4 class · 4 ไฟล์

> อ่าน [00-shared.md](00-shared.md) ก่อน (กติกาการตั้งชื่อ, ตัวแปร 4 แบบ, Enum, Error, DTO)

## สรุปงาน

- **ไฟล์ที่ต้องเขียน:** `app/services/focus_service.py`, `ui/focus/stopwatch_timer.py`, `ui/focus/egg_view.py`, `ui/focus/focus_view.py`
- **method ในไฟล์ของคนอื่นที่ต้องเขียนด้วย:** `StudySession` ใน `app/domain/study_session.py`
- **ต้องใช้ของ:** P2 (`Clock`, `GameStore`, `StudySession`), P3 (`BaseView`, `ConfirmDialog`), P5 (`EggFactory`), P7 (`CpegoBot`, `CpegoBubble`, `EggChoicePopup`)
- **คนที่ใช้ของเรา:** P7 ใส่ bubble และ popup ลงในหน้า Focus · P8 ใช้ `can_hatch()`, `mark_hatched()` · P9 ใช้ `is_success()`
- **ส่งงาน:** branch `feat/focus-session` → PR ให้เพื่อนรีวิว 1 คน

## Class ที่ต้องเขียน

### `FocusSessionService`

*class* · `app/services/focus_service.py`

เริ่ม / ดูเวลา / หยุด การอ่าน

**สร้าง:** `FocusSessionService(store, clock, settings)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง (GameStore) |
| `clock` | `Clock` | ต้องส่งตอนสร้าง | นาฬิกากลาง |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | ค่าตั้งค่า |
| `factory` | `EggFactory` | สร้างใน `__init__` = `EggFactory()` | หา unlocked_tiers |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `start(subject: str)` | `SessionDTO` | subject ว่าง raise ValidationError(field="subject") · มี RUNNING อยู่ raise InvalidStateError |
| `get_running()` | `SessionDTO \| None` | session ที่ค้างอยู่ |
| `elapsed(session_id: int)` | `int` | วินาทีเกมที่อ่านไปแล้ว (ผ่าน clock) |
| `stop(session_id: int)` | `StopResult` | หยุดและตัดสินผล |

### `StopwatchTimer`

*class* · `ui/focus/stopwatch_timer.py`

นาฬิกานับขึ้น tick ทุก interval_sec แล้วเรียก on_tick(elapsed_sec)

**สร้าง:** `StopwatchTimer(clock, started_at, on_tick, interval_sec=1.0)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `clock` | `Clock` | ต้องส่งตอนสร้าง | นาฬิกากลาง |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `on_tick` | `Callable[[int], None]` | ต้องส่งตอนสร้าง | เรียกทุก tick |
| `interval_sec` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1.0` | ระยะ tick |
| `running` | `bool` | สร้างใน `__init__` = `False` | เดินอยู่ไหม |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `start(page: ft.Page)` | `None` | เริ่ม loop ด้วย page.run_task |
| `stop()` | `None` | หยุด |
| `elapsed_sec` *property* | `int` | clock.elapsed_sec(started_at) |
| `format(seconds: int)` *staticmethod* | `str` | "67:07" (นาที:วินาที) |

### `EggView`

*class* · สืบทอดจาก `BaseWidget` · `ui/focus/egg_view.py`

รูปไข่กลางจอ เปลี่ยนรูปตามระดับที่ปลดล็อก

**สร้าง:** `EggView(tier=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tier` | `EggTier \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | None = ยังไม่ถึง 15 นาที |
| `image` | `ft.Image \| None` | สร้างใน `__init__` = `None` | รูป |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `set_tier(tier: EggTier \| None)` | `None` | เปลี่ยนรูป |
| `wobble()` | `None` | ไข่ขยับตอนปลดล็อกระดับใหม่ |

### `FocusView`

*class* · สืบทอดจาก `BaseView` · `ui/focus/focus_view.py`

หน้า ③ Focus: นาฬิกา + ไข่ + CPEGO bubble + ปุ่ม STOP

**สร้าง:** `FocusView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/focus"` | path ของหน้า |
| `session` | `SessionDTO \| None` | สร้างใน `__init__` = `None` | session ที่อ่าน |
| `timer` | `StopwatchTimer \| None` | สร้างใน `__init__` = `None` | นาฬิกา |
| `time_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความ 67:07 |
| `egg_view` | `EggView \| None` | สร้างใน `__init__` = `None` | รูปไข่ |
| `bot` | `CpegoBot \| None` | สร้างใน `__init__` = `None` | P7 |
| `bubble` | `CpegoBubble \| None` | สร้างใน `__init__` = `None` | P7 |
| `confirm` | `ConfirmDialog \| None` | สร้างใน `__init__` = `None` | Are you sure to stop? |
| `egg_choice` | `EggChoicePopup \| None` | สร้างใน `__init__` = `None` | P7 |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `on_enter()` | `None` | โหลด session, เริ่ม timer, bubble ทักทาย |
| `on_leave()` | `None` | หยุด timer |
| `on_tick(elapsed_sec: int)` | `None` | อัปเดตเวลา, bot.check → bubble.show, egg_view.set_tier |
| `ask_stop()` | `None` | เปิด ConfirmDialog |
| `confirm_stop()` | `None` | focus.stop · FAILED → /hatch (โชว์ผลไม่สำเร็จ) · READY → เปิด EggChoicePopup |
| `on_egg_chosen(tier: EggTier)` | `None` | ไป /hatch พร้อม session_id, tier |

## Method ที่ต้องเขียนในไฟล์ของคนอื่น

### `StudySession`

*class* · `app/domain/study_session.py`

การอ่านหนึ่งรอบ · P2 สร้างตัวแปร, P6 เขียน method (encapsulation: เปลี่ยน status ผ่าน method เท่านั้น)

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `stop(ended_at: datetime, duration_sec: int, min_success_sec: int)` | `SessionStatus` | บันทึกเวลา แล้วเปลี่ยนเป็น FAILED หรือ READY_TO_HATCH · ถ้าไม่ได้ RUNNING ให้ raise InvalidStateError |
| `can_hatch()` | `bool` | True ถ้า READY_TO_HATCH |
| `mark_hatched(tier: EggTier, species_code: str)` | `None` | บันทึกไข่ + สัตว์ เปลี่ยนเป็น HATCHED |
| `is_success()` | `bool` | True ถ้า HATCHED |
| `to_dto()` | `SessionDTO` | แปลงเป็น SessionDTO |
