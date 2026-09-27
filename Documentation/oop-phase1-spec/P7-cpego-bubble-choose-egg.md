# P7 · CPEGO bubble + Choose egg

Phase 1 · bubble แจ้ง milestone, popup เลือกไข่ · 5 class · 3 ไฟล์

> อ่าน [00-shared.md](00-shared.md) ก่อน (กติกาการตั้งชื่อ, ตัวแปร 4 แบบ, Enum, Error, DTO)

## สรุปงาน

- **ไฟล์ที่ต้องเขียน:** `ui/focus/cpego_bot.py`, `ui/focus/cpego_bubble.py`, `ui/focus/egg_choice_popup.py`
- **ต้องใช้ของ:** P3 (`BaseWidget`, `Popup`, `ConfirmDialog`), P5 (`TierService` ให้ข้อมูลไข่)
- **คนที่ใช้ของเรา:** P6 เรียกใช้ในหน้า Focus
- **ส่งงาน:** branch `feat/cpego-bubble-choose-egg` → PR ให้เพื่อนรีวิว 1 คน

## Class ที่ต้องเขียน

### `CpegoMessage`

*dataclass (แก้ค่าไม่ได้)* · `ui/focus/cpego_bot.py`

ข้อความหนึ่งอันของ CPEGO

**สร้าง:** `CpegoMessage(text=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `text` | `str` | ต้องส่งตอนสร้าง | ข้อความ |
| `kind` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"info"` | "greeting" \| "milestone" \| "info" |

### `CpegoBot`

*class* · `ui/focus/cpego_bot.py`

ตัดสินว่าเมื่อไหร่ CPEGO ต้องพูดอะไร (ส่งครั้งเดียวต่อ milestone)

**สร้าง:** `CpegoBot(tiers)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `tiers` | `list[TierInfo]` | ต้องส่งตอนสร้าง | ใช้ required_minutes เป็น milestone |
| `_sent_minutes` | `set[int]` | สร้างใน `__init__` = `set()` | milestone ที่พูดไปแล้ว |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `greeting(subject: str)` | `CpegoMessage` | ข้อความทักตอนเริ่ม |
| `check(elapsed_sec: int)` | `CpegoMessage \| None` | เพิ่งผ่าน milestone ไหม ถ้าผ่านคืนข้อความ เช่น "อ่านครบ 15 นาทีแล้ว ได้ไข่รุ่นเรา!" |
| `reset()` | `None` | ล้างสถานะ |

### `CpegoBubble`

*class* · สืบทอดจาก `BaseWidget` · `ui/focus/cpego_bubble.py`

bubble CPEGO เด้งมุมจอแล้วหายเองตาม show_sec

**สร้าง:** `CpegoBubble(show_sec=5.0)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `show_sec` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `5.0` | โชว์กี่วินาที |
| `visible` | `bool` | สร้างใน `__init__` = `False` | โชว์อยู่ไหม |
| `text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความ |
| `_hide_task` | `Any` | สร้างใน `__init__` = `None` | task ที่จะซ่อน bubble |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง (รูป CPEGO + กล่องข้อความ) |
| `show(page: ft.Page, message: CpegoMessage)` | `None` | โชว์แล้วตั้งเวลาซ่อน ถ้ามีข้อความใหม่มาทับให้เริ่มนับใหม่ |
| `hide()` | `None` | ซ่อน |

### `EggChoiceCard`

*class* · สืบทอดจาก `BaseWidget` · `ui/focus/egg_choice_popup.py`

การ์ดไข่หนึ่งระดับ ถ้าล็อกเป็นสีเทากดไม่ได้

**สร้าง:** `EggChoiceCard(info, locked, on_select, selected=False)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `info` | `TierInfo` | ต้องส่งตอนสร้าง | ข้อมูลไข่ |
| `locked` | `bool` | ต้องส่งตอนสร้าง | ยังไม่ปลดล็อก |
| `on_select` | `Callable[[EggTier], None]` | ต้องส่งตอนสร้าง | กดเลือก |
| `selected` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `False` | ถูกเลือกอยู่ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างการ์ด |
| `set_selected(selected: bool)` | `None` | เปลี่ยน highlight |

### `EggChoicePopup`

*class* · สืบทอดจาก `BaseWidget` · `ui/focus/egg_choice_popup.py`

popup Choose an egg: Total time + การ์ดไข่ 3 ระดับ + ยืนยัน

**สร้าง:** `EggChoicePopup(result, tiers, on_confirm)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `result` | `StopResult` | ต้องส่งตอนสร้าง | ผลหลัง stop |
| `tiers` | `list[TierInfo]` | ต้องส่งตอนสร้าง | ไข่ทุกระดับ |
| `on_confirm` | `Callable[[EggTier], None]` | ต้องส่งตอนสร้าง | ยืนยันเลือกไข่ |
| `cards` | `list[EggChoiceCard]` | สร้างใน `__init__` = `[]` | การ์ดไข่ทุกใบ |
| `selected_tier` | `EggTier \| None` | สร้างใน `__init__` = `None` | ไข่ที่กด |
| `confirm` | `ConfirmDialog \| None` | สร้างใน `__init__` = `None` | Are you sure to choose ...? |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง (เลือกไข่สูงสุดที่ปลดล็อกไว้ให้ก่อน) |
| `select(tier: EggTier)` | `None` | เลือกการ์ด |
| `ask_confirm(page: ft.Page)` | `None` | เปิด ConfirmDialog |
| `open(page: ft.Page)` | `None` | เปิด popup |
