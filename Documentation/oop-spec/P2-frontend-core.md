# P2 · Frontend Core

AppContext, Navigator, BaseView, widget กลาง, Theme, หน้า Landing

> อ่าน [00-shared.md](00-shared.md) ก่อน: กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **Backend (0 class):** ไม่มี
- **Frontend (15 class):** `BaseWidget`, `BaseView`, `Navigator`, `AppContext`, `Theme`, `SoundManager`, `PixelButton`, `Popup`, `ConfirmDialog`, `StatTile`, `Format`, `HowToSlide`, `HowToPopup`, `PlayerPicker`, `LandingView`
- **ใช้ของใคร:** P1 (`PlayerService`, `GameStore`, `Clock`, `Settings`) · import service ของทุกคนมาใส่ใน `AppContext`
- **ใครใช้ของเรา:** ทุกคนที่ทำหน้าจอ
- **branch:** `feat/frontend-core`

## Frontend

**Import ที่ต้องใช้ (รวมทุกไฟล์ frontend ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, TYPE_CHECKING

import flet as ft
import flet_audio as fta

from app.config import Settings
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.domain.enums import EggTier, Rarity
from app.dto import PlayerDTO
from app.errors import AppError, InvalidStateError, ValidationError
from app.services.analytics_service import AnalyticsService
from app.services.dex_service import DexService
from app.services.focus_service import FocusSessionService
from app.services.hatch_service import HatchService
from app.services.player_service import PlayerService
from app.services.room_service import RoomService
from app.services.sanctuary_service import SanctuaryService
from app.services.tier_service import TierService
from ui.dex.dex_view import DexView
from ui.focus.focus_view import FocusView
from ui.hatch.hatch_view import HatchView
from ui.lobby.lobby_view import LobbyView
from ui.result.history_view import HistoryView
from ui.result.result_view import ResultView
from ui.room.room_focus_view import RoomFocusView
from ui.room.room_setup_view import RoomSetupView
```

### `BaseWidget`

- **ไฟล์:** `ui/core/base_widget.py`
- **ชนิด:** abstract class
- **inherit:** ไม่มี (เป็น `ABC`)
- **หน้าที่:** แม่ของ widget ทุกตัว ห่อ Flet control ไว้ข้างใน คืนผ่าน build()

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_control` | `ft.Control \| None` | สร้างใน `__init__` = `None` | cache ของ control |

| method | return | ทำอะไร |
|---|---|---|
| `build()` *abstract* | `ft.Control` | สร้าง Flet control |
| `control` *@property* | `ft.Control` | build ครั้งแรกแล้วเก็บไว้ |
| `refresh()` | `None` | เรียก control.update() หลังเปลี่ยนค่า |

### `BaseView`

- **ไฟล์:** `ui/core/base_view.py`
- **ชนิด:** abstract class
- **inherit:** ไม่มี (เป็น `ABC`)
- **สร้าง:** `BaseView(ctx, **params)`
- **หน้าที่:** แม่ของทุกหน้า Navigator เรียก to_view() ตอนเปลี่ยนหน้า

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/"` | path ของหน้า |
| `requires_player` | `bool` | ค่าคงที่ของ class `= True` | False เฉพาะหน้า Landing |
| `ctx` | `AppContext` | ต้องส่งตอนสร้าง | ของกลาง |
| `params` | `dict[str, Any]` | สร้างใน `__init__` = `dict(params)` | ค่าที่ส่งมากับ nav.go เช่น session_id |

| method | return | ทำอะไร |
|---|---|---|
| `build()` *abstract* | `ft.Control` | สร้างเนื้อหาหน้า |
| `on_enter()` | `None` | เรียกหลังหน้าแสดง |
| `on_leave()` | `None` | เรียกก่อนออกจากหน้า |
| `show_error(error: AppError)` | `None` | โชว์ SnackBar สีแดง |
| `to_view()` | `ft.View` | ห่อ build() เป็น ft.View(route, [...]) |

### `Navigator`

- **ไฟล์:** `ui/core/navigator.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `Navigator(ctx)`
- **หน้าที่:** สลับหน้า ถ้ายังไม่เลือกผู้เล่นเด้งไป "/"

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `ctx` | `AppContext` | ต้องส่งตอนสร้าง | ของกลาง |
| `routes` | `dict[str, type[BaseView]]` | สร้างใน `__init__` = `{}` | route → class |
| `current` | `BaseView \| None` | สร้างใน `__init__` = `None` | หน้าที่เปิดอยู่ |

| method | return | ทำอะไร |
|---|---|---|
| `register(view_cls: type[BaseView])` | `None` | ลงทะเบียนหน้า |
| `start()` | `None` | register ทุกหน้า (ตารางเส้นทางใน 00-shared) แล้วเปิด "/" |
| `go(route: str, **params: Any)` | `None` | on_leave หน้าเก่า → สร้างหน้าใหม่ → on_enter |

### `AppContext`

- **ไฟล์:** `ui/core/app_context.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `AppContext(page, settings, store)`
- **หน้าที่:** ของกลางที่ทุกหน้าใช้ หน้าจอเรียก backend ผ่านที่นี่เท่านั้น

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `page` | `ft.Page` | ต้องส่งตอนสร้าง | หน้าต่าง Flet |
| `settings` | `Settings` | ต้องส่งตอนสร้าง | ค่าตั้งค่า |
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง |
| `clock` | `Clock` | สร้างใน `__init__` = `Clock(settings.demo_speed)` | นาฬิกากลาง |
| `player` | `PlayerDTO \| None` | สร้างใน `__init__` = `None` | ผู้เล่นที่เลือกอยู่ |
| `players` | `PlayerService` | สร้างใน `__init__` = `PlayerService(store, self.clock)` | P1 |
| `tiers` | `TierService` | สร้างใน `__init__` = `TierService()` | P3 |
| `focus` | `FocusSessionService` | สร้างใน `__init__` = `FocusSessionService(store, self.clock, settings)` | P4 |
| `hatch` | `HatchService` | สร้างใน `__init__` = `HatchService(store)` | P3 |
| `rooms` | `RoomService` | สร้างใน `__init__` = `RoomService(store, self.clock, settings, self.hatch)` | P5 |
| `sanctuary` | `SanctuaryService` | สร้างใน `__init__` = `SanctuaryService(store)` | P6 |
| `dex` | `DexService` | สร้างใน `__init__` = `DexService(store)` | P6 |
| `analytics` | `AnalyticsService` | สร้างใน `__init__` = `AnalyticsService(store, settings)` | P7 |
| `sound` | `SoundManager` | สร้างใน `__init__` = `SoundManager(page)` | P2 |
| `nav` | `Navigator` | สร้างใน `__init__` = `Navigator(self)` | P2 |

| method | return | ทำอะไร |
|---|---|---|
| `create(page: ft.Page, settings: Settings)` *@classmethod* | `AppContext` | GameStore.open(settings) แล้วคืน AppContext |
| `require_player()` | `PlayerDTO` | คืน player ถ้ายังไม่เลือก → InvalidStateError |

### `Theme`

- **ไฟล์:** `ui/core/theme.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `Theme()`
- **หน้าที่:** สีและฟอนต์ เอาค่าจาก Figma มาใส่ที่นี่ที่เดียว

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `PRIMARY` | `str` | ค่าคงที่ของ class `= "#2F5BD8"` | สีหลัก |
| `ACCENT` | `str` | ค่าคงที่ของ class `= "#F2913A"` | สีเน้น |
| `BACKGROUND` | `str` | ค่าคงที่ของ class `= "#FFFFFF"` | พื้นหลัง |
| `TEXT` | `str` | ค่าคงที่ของ class `= "#1D2333"` | ตัวอักษร |
| `MUTED` | `str` | ค่าคงที่ของ class `= "#8A93A6"` | ของที่ล็อก/สีเทา |
| `ERROR` | `str` | ค่าคงที่ของ class `= "#D2412F"` | error |
| `FONT_FAMILY` | `str` | ค่าคงที่ของ class `= "Mali"` | ฟอนต์ |
| `MOBILE_BREAKPOINT` | `int` | ค่าคงที่ของ class `= 600` | px |

| method | return | ทำอะไร |
|---|---|---|
| `apply(page: ft.Page)` *@classmethod* | `None` | ตั้งฟอนต์ สี ขนาดหน้าต่าง |
| `is_mobile(page: ft.Page)` *@classmethod* | `bool` | page.width < MOBILE_BREAKPOINT |
| `rarity_color(rarity: Rarity)` *@classmethod* | `str` | สีของแต่ละ rarity ใช้ร่วมกันทุกหน้า |

### `SoundManager`

- **ไฟล์:** `ui/core/sound_manager.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `SoundManager(page, muted=False)`
- **หน้าที่:** เล่นเสียง SFX (package flet-audio)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `page` | `ft.Page` | ต้องส่งตอนสร้าง | หน้าต่าง Flet |
| `muted` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `False` | ปิดเสียงไหม |
| `_sounds` | `dict[str, Any]` | สร้างใน `__init__` = `{}` | ชื่อ → ตัวเล่นเสียง |

| method | return | ทำอะไร |
|---|---|---|
| `load(name: str, path: str)` | `None` | เช่น load("tada", "sfx/tada.mp3") |
| `play(name: str)` | `None` | muted แล้วไม่เล่น |
| `toggle_mute()` | `bool` | สลับ คืนค่าใหม่ |

### `PixelButton`

- **ไฟล์:** `ui/core/widgets.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `PixelButton(text, on_click, variant="primary", disabled=False)`
- **หน้าที่:** ปุ่มสไตล์เดียวกันทั้งแอป

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `text` | `str` | ต้องส่งตอนสร้าง | ข้อความ |
| `on_click` | `Callable[[], None]` | ต้องส่งตอนสร้าง | ฟังก์ชันตอนกด |
| `variant` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"primary"` | "primary" \| "secondary" \| "danger" |
| `disabled` | `bool` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `False` | กดไม่ได้ |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `set_disabled(disabled: bool)` | `None` | ทำตาม class แม่ |

### `Popup`

- **ไฟล์:** `ui/core/widgets.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `Popup(title, content, on_close=None)`
- **หน้าที่:** กรอบ popup กลางจอ หัวข้อ + ปุ่ม X

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `title` | `str` | ต้องส่งตอนสร้าง | หัวข้อ |
| `content` | `ft.Control` | ต้องส่งตอนสร้าง | เนื้อหาข้างใน |
| `on_close` | `Callable[[], None] \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | มีแล้วโชว์ปุ่ม X |
| `is_open` | `bool` | สร้างใน `__init__` = `False` | เปิดอยู่ไหม |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `open(page: ft.Page)` | `None` | ทำตาม class แม่ |
| `close(page: ft.Page)` | `None` | ทำตาม class แม่ |

### `ConfirmDialog`

- **ไฟล์:** `ui/core/widgets.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `ConfirmDialog(title, on_yes, on_no=None)`
- **หน้าที่:** กล่อง YES / NO

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `title` | `str` | ต้องส่งตอนสร้าง | คำถาม |
| `on_yes` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กด YES |
| `on_no` | `Callable[[], None] \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | กด NO |
| `_dialog` | `ft.AlertDialog \| None` | สร้างใน `__init__` = `None` | dialog ที่สร้างแล้ว |

| method | return | ทำอะไร |
|---|---|---|
| `open(page: ft.Page)` | `None` | ทำตาม class แม่ |
| `close(page: ft.Page)` | `None` | ทำตาม class แม่ |

### `StatTile`

- **ไฟล์:** `ui/core/widgets.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `StatTile(label, value)`
- **หน้าที่:** กล่องตัวเลขหนึ่งค่า (ใช้ในหน้า Result, History, Dex)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `label` | `str` | ต้องส่งตอนสร้าง | เช่น "เวลาอ่านรวม" |
| `value` | `str` | ต้องส่งตอนสร้าง | เช่น "3 ชม. 20 นาที" |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |

### `Format`

- **ไฟล์:** `ui/core/format.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `Format()`
- **หน้าที่:** แปลงค่าเป็นข้อความให้ทุกหน้าใช้แบบเดียวกัน

| method | return | ทำอะไร |
|---|---|---|
| `clock(seconds: int)` *@staticmethod* | `str` | "67:07" (นาที:วินาที) |
| `duration(seconds: int)` *@staticmethod* | `str` | "1 ชม. 7 นาที" |
| `percent(value: float)` *@staticmethod* | `str` | 0.425 → "42.5%" |
| `tier_name(tier: EggTier)` *@staticmethod* | `str` | "ไข่รุ่นพี่" |

### `HowToSlide`

- **ไฟล์:** `ui/landing/howto_popup.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `HowToSlide(image_path=..., text=...)`
- **หน้าที่:** หนึ่งหน้าของ How to Play

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `image_path` | `str` | ต้องส่งตอนสร้าง | รูปไข่ |
| `text` | `str` | ต้องส่งตอนสร้าง | ข้อความ |

### `HowToPopup`

- **ไฟล์:** `ui/landing/howto_popup.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `HowToPopup(slides, on_close)`
- **หน้าที่:** popup How to Play แบบ slideshow

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `slides` | `list[HowToSlide]` | ต้องส่งตอนสร้าง | หน้าทั้งหมด |
| `on_close` | `Callable[[], None]` | ต้องส่งตอนสร้าง | กดปิด |
| `current_index` | `int` | สร้างใน `__init__` = `0` | ลำดับที่โชว์อยู่ |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `next()` | `None` | ทำตาม class แม่ |
| `prev()` | `None` | ทำตาม class แม่ |
| `default_slides()` *@staticmethod* | `list[HowToSlide]` | เนื้อหา How to ของเกม |

### `PlayerPicker`

- **ไฟล์:** `ui/landing/player_picker.py`
- **ชนิด:** class
- **inherit:** `BaseWidget`
- **สร้าง:** `PlayerPicker(players, on_pick, on_create)`
- **หน้าที่:** เลือกผู้เล่นที่มีอยู่ หรือพิมพ์ชื่อเล่นใหม่

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `players` | `list[PlayerDTO]` | ต้องส่งตอนสร้าง | ผู้เล่นทั้งหมด |
| `on_pick` | `Callable[[PlayerDTO], None]` | ต้องส่งตอนสร้าง | เลือกคนที่มีอยู่ |
| `on_create` | `Callable[[str], None]` | ต้องส่งตอนสร้าง | กดสร้างชื่อใหม่ |
| `nickname_field` | `ft.TextField \| None` | สร้างใน `__init__` = `None` | ช่องชื่อเล่น |
| `error_text` | `ft.Text \| None` | สร้างใน `__init__` = `None` | ข้อความเตือนสีแดง |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | รายชื่อ + ช่องชื่อใหม่ + ปุ่ม CREATE |
| `show_error(message: str)` | `None` | ทำตาม class แม่ |

### `LandingView`

- **ไฟล์:** `ui/landing/landing_view.py`
- **ชนิด:** class
- **inherit:** `BaseView`
- **สร้าง:** `LandingView(ctx, **params)`
- **หน้าที่:** หน้าแรก: โลโก้, ชื่อเกม, เลือก/สร้างผู้เล่น, HOW TO

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `route` | `str` | ค่าคงที่ของ class `= "/"` | path ของหน้า |
| `requires_player` | `bool` | ค่าคงที่ของ class `= False` | - |
| `picker` | `PlayerPicker \| None` | สร้างใน `__init__` = `None` | ตัวเลือกผู้เล่น |
| `howto` | `HowToPopup \| None` | สร้างใน `__init__` = `None` | popup How to |

| method | return | ทำอะไร |
|---|---|---|
| `build()` | `ft.Control` | ทำตาม class แม่ |
| `pick_player(player: PlayerDTO)` | `None` | ctx.player = player แล้วไป /lobby |
| `create_player(nickname: str)` | `None` | ctx.players.create_player · ValidationError → picker.show_error |
| `open_howto()` | `None` | ทำตาม class แม่ |

## เช็กลิสต์ก่อนส่ง PR

- [ ] เปิดแอปแล้วเข้าหน้า Landing ได้
- [ ] สร้างผู้เล่นใหม่แล้วไป /lobby
- [ ] nav.go ไปหน้าที่ไม่ได้เลือกผู้เล่นต้องเด้งกลับ /
- [ ] Format.clock(4027) == "67:07"
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
