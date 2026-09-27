# P1 · Landing + How to + Theme

Phase 1 · หน้า ① Landing, popup How to Play, สี/ฟอนต์, เสียง · 5 class · 4 ไฟล์

> อ่าน [00-shared.md](00-shared.md) ก่อน (กติกาการตั้งชื่อ, ตัวแปร 4 แบบ, Enum, Error, DTO)

## สรุปงาน

- **ไฟล์ที่ต้องเขียน:** `ui/core/theme.py`, `ui/core/sound_manager.py`, `ui/landing/howto_popup.py`, `ui/landing/landing_view.py`
- **ต้องใช้ของ:** P3 (`BaseView`, `BaseWidget`, `Popup`, `PixelButton`)
- **คนที่ใช้ของเรา:** P4 ใช้ `HowToPopup` ในหน้า Lobby · ทุกคนใช้ `Theme`
- **ส่งงาน:** branch `feat/landing-how-to-theme` → PR ให้เพื่อนรีวิว 1 คน

## Class ที่ต้องเขียน

### `Theme`

*class* · `ui/core/theme.py`

สีและฟอนต์ของแอป เอาค่าจาก Figma มาใส่ที่นี่ที่เดียว

**สร้าง:** `Theme()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `PRIMARY` | `str` | ค่าคงที่ของ class `= "#2F5BD8"` | สีหลัก |
| `ACCENT` | `str` | ค่าคงที่ของ class `= "#F2913A"` | สีเน้น |
| `BACKGROUND` | `str` | ค่าคงที่ของ class `= "#FFFFFF"` | พื้นหลัง |
| `TEXT` | `str` | ค่าคงที่ของ class `= "#1D2333"` | ตัวอักษร |
| `ERROR` | `str` | ค่าคงที่ของ class `= "#D2412F"` | error |
| `FONT_FAMILY` | `str` | ค่าคงที่ของ class `= "Mali"` | ฟอนต์ |
| `MOBILE_BREAKPOINT` | `int` | ค่าคงที่ของ class `= 600` | กว้างน้อยกว่านี้ใช้ layout มือถือ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `apply(page: ft.Page)` *classmethod* | `None` | ตั้งฟอนต์และสีให้ page |
| `is_mobile(page: ft.Page)` *classmethod* | `bool` | จอแคบกว่า MOBILE_BREAKPOINT ไหม |

### `SoundManager`

*class* · `ui/core/sound_manager.py`

เล่นเสียง SFX (ใช้ package flet-audio)

**สร้าง:** `SoundManager(page, muted=False)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `page` | `ft.Page` | ต้องส่งตอนสร้าง | หน้าต่าง |
| `muted` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `False` | ปิดเสียงไหม |
| `_sounds` | `dict[str, Any]` | สร้างใน `__init__` = `{}` | ชื่อ → ตัวเล่นเสียง |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `load(name: str, path: str)` | `None` | โหลดเสียง เช่น load("tada", "sfx/tada.mp3") |
| `play(name: str)` | `None` | เล่น (ถ้า muted ไม่ต้องเล่น) |
| `toggle_mute()` | `bool` | สลับ คืนค่าใหม่ |

### `HowToSlide`

*dataclass (แก้ค่าไม่ได้)* · `ui/landing/howto_popup.py`

หนึ่งหน้าของ How to Play

**สร้าง:** `HowToSlide(image_path=..., text=...)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `image_path` | `str` | ต้องส่งตอนสร้าง | รูป |
| `text` | `str` | ต้องส่งตอนสร้าง | คำอธิบาย |

### `HowToPopup`

*class* · สืบทอดจาก `BaseWidget` · `ui/landing/howto_popup.py`

popup How to Play แบบ slideshow ใช้ทั้งหน้า Landing และ Lobby

**สร้าง:** `HowToPopup(slides, on_close)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `slides` | `list[HowToSlide]` | ต้องส่งตอนสร้าง | หน้าทั้งหมด |
| `on_close` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กดปิด |
| `current_index` | `int` | สร้างใน `__init__` = `0` | หน้าที่โชว์ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง |
| `next()` | `None` | หน้าถัดไป |
| `prev()` | `None` | หน้าก่อน |
| `show(index: int)` | `None` | ไปหน้าที่ index |
| `default_slides()` *staticmethod* | `list[HowToSlide]` | เนื้อหา How to ของเกม |

### `LandingView`

*class* · สืบทอดจาก `BaseView` · `ui/landing/landing_view.py`

หน้า ① Landing: โลโก้, ชื่อเกม, ปุ่ม START, ปุ่ม HOW TO

**สร้าง:** `LandingView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/"` | path ของหน้า |
| `howto` | `HowToPopup \| None` | สร้างใน `__init__` = `None` | popup How to |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างหน้า |
| `start()` | `None` | ไป /lobby |
| `open_howto()` | `None` | เปิด HowToPopup |
