# P3 · Frontend core

Phase 1 · AppContext, Navigator, BaseView, widget กลาง · 7 class · 5 ไฟล์

> อ่าน [00-shared.md](00-shared.md) ก่อน (กติกาการตั้งชื่อ, ตัวแปร 4 แบบ, Enum, Error, DTO)

## สรุปงาน

- **ไฟล์ที่ต้องเขียน:** `ui/core/base_widget.py`, `ui/core/base_view.py`, `ui/core/navigator.py`, `ui/core/app_context.py`, `ui/core/widgets.py`
- **ต้องใช้ของ:** ไม่มี · ต้องเสร็จก่อน เพราะทุกหน้าใช้ `BaseView`, `BaseWidget`, `Navigator`, `AppContext`
- **คนที่ใช้ของเรา:** ทุกคน
- **ส่งงาน:** branch `feat/frontend-core` → PR ให้เพื่อนรีวิว 1 คน

## Class ที่ต้องเขียน

### `BaseWidget`

*abstract class* · `ui/core/base_widget.py`

แม่ของ widget ทุกตัว ห่อ Flet control ไว้ข้างใน แล้วคืนผ่าน build()

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_control` | `ft.Control \| None` | สร้างใน `__init__` = `None` | cache ของ control |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` *abstract* | `ft.Control` | สร้าง Flet control |
| `control` *property* | `ft.Control` | build ครั้งแรกแล้วเก็บไว้ |
| `refresh()` | `None` | สั่ง update() หลังเปลี่ยนค่า |

### `BaseView`

*abstract class* · `ui/core/base_view.py`

แม่ของทุกหน้า (4 หน้า) Navigator เรียก to_view() ตอนเปลี่ยนหน้า

**สร้าง:** `BaseView(ctx, **params)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/"` | path ของหน้า |
| `ctx` | `AppContext` | ต้องส่งตอนสร้าง | ของกลาง |
| `params` | `dict[str, Any]` | สร้างใน `__init__` = `dict(params)` | ค่าที่ส่งมากับ nav.go เช่น session_id |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` *abstract* | `ft.Control` | สร้างเนื้อหาของหน้า |
| `on_enter()` | `None` | เรียกหลังหน้าแสดง |
| `on_leave()` | `None` | เรียกก่อนออกจากหน้า |
| `show_error(error: AppError)` | `None` | โชว์ SnackBar |
| `to_view()` | `ft.View` | ห่อ build() เป็น ft.View |

### `Navigator`

*class* · `ui/core/navigator.py`

สลับหน้า: "/" Landing, "/lobby", "/focus", "/hatch"

**สร้าง:** `Navigator(ctx)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `ctx` | `AppContext` | ต้องส่งตอนสร้าง | ของกลาง |
| `routes` | `dict[str, type[BaseView]]` | สร้างใน `__init__` = `{}` | route → class |
| `current` | `BaseView \| None` | สร้างใน `__init__` = `None` | หน้าที่เปิดอยู่ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `register(view_cls: type[BaseView])` | `None` | ลงทะเบียนหน้า |
| `start()` | `None` | register 4 หน้า แล้วเปิด "/" |
| `go(route: str, **params: Any)` | `None` | เปลี่ยนหน้า (on_leave เก่า, on_enter ใหม่) |

### `AppContext`

*class* · `ui/core/app_context.py`

ของกลางที่ทุกหน้าใช้ หน้าจอเรียก backend ผ่านที่นี่เท่านั้น

**สร้าง:** `AppContext(page, settings, store)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `page` | `ft.Page` | ต้องส่งตอนสร้าง | หน้าต่าง Flet |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | ค่าตั้งค่า |
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูล |
| `clock` | `Clock` | สร้างใน `__init__` = `Clock(settings.demo_speed)` | นาฬิกากลาง |
| `tiers` | `TierService` | สร้างใน `__init__` = `TierService()` | P5 |
| `focus` | `FocusSessionService` | สร้างใน `__init__` = `FocusSessionService(store, self.clock, settings)` | P6 |
| `hatch` | `HatchService` | สร้างใน `__init__` = `HatchService(store)` | P8 |
| `sanctuary` | `SanctuaryService` | สร้างใน `__init__` = `SanctuaryService(store)` | P4 |
| `results` | `ResultService` | สร้างใน `__init__` = `ResultService(store, settings)` | P9 |
| `sound` | `SoundManager` | สร้างใน `__init__` = `SoundManager(page)` | P1 |
| `nav` | `Navigator` | สร้างใน `__init__` = `Navigator(self)` | P3 |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `create(page: ft.Page, settings: Settings)` *classmethod* | `AppContext` | GameStore.create_in_memory แล้วคืน AppContext |

### `PixelButton`

*class* · สืบทอดจาก `BaseWidget` · `ui/core/widgets.py`

ปุ่มสไตล์เดียวกันทั้งแอป

**สร้าง:** `PixelButton(text, on_click, variant="primary", disabled=False)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `text` | `str` | ต้องส่งตอนสร้าง | ข้อความบนปุ่ม |
| `on_click` | `Callable[[], None]` | ต้องส่งตอนสร้าง | ฟังก์ชันตอนกด |
| `variant` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"primary"` | "primary" \| "secondary" \| "danger" |
| `disabled` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `False` | กดไม่ได้ |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้างปุ่ม |
| `set_disabled(disabled: bool)` | `None` | เปิด/ปิดการกด |

### `Popup`

*class* · สืบทอดจาก `BaseWidget` · `ui/core/widgets.py`

กรอบ popup กลางจอ มีหัวข้อ + ปุ่ม X (How to, Setup, Choose egg ใช้ตัวนี้)

**สร้าง:** `Popup(title, content, on_close=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `title` | `str` | ต้องส่งตอนสร้าง | หัวข้อ |
| `content` | `ft.Control` | ต้องส่งตอนสร้าง | เนื้อหา |
| `on_close` | `Callable[[], None] \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ถ้ามี จะโชว์ปุ่ม X |
| `is_open` | `bool` | สร้างใน `__init__` = `False` | เปิดอยู่ไหม |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `build()` | `ft.Control` | สร้าง popup |
| `open(page: ft.Page)` | `None` | เปิด |
| `close(page: ft.Page)` | `None` | ปิด |

### `ConfirmDialog`

*class* · `ui/core/widgets.py`

กล่องถาม YES / NO

**สร้าง:** `ConfirmDialog(title, on_yes, on_no=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `title` | `str` | ต้องส่งตอนสร้าง | คำถาม เช่น "Are you sure to stop?" |
| `on_yes` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กด YES |
| `on_no` | `Callable[[], None] \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | กด NO |
| `_dialog` | `ft.AlertDialog \| None` | สร้างใน `__init__` = `None` | dialog ที่สร้างแล้ว |

| method | คืนค่า (return) | หน้าที่ |
|---|---|---|
| `open(page: ft.Page)` | `None` | เปิด |
| `close(page: ft.Page)` | `None` | ปิด |
