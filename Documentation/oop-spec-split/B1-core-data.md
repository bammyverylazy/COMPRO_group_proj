# B1 · Core Data (Backend)

Settings, Clock, model, ที่เก็บข้อมูล save.json, ผู้เล่น

> อ่าน [00-shared.md](00-shared.md) ก่อน: วิธีทำงานแบบแยกฝั่ง, กติกาไข่, เส้นทางหน้าจอ, การตั้งชื่อ, clean code, Enum, Error, DTO

## สรุปงาน

- **ฝั่ง:** Backend อย่างเดียว · ไม่ต้อง import flet
- **Class ที่ต้องเขียน (17):** `Settings`, `Clock`, `Player`, `Species`, `StudySession`, `OwnedPet`, `GroupRoom`, `BaseRepository`, `PlayerRepository`, `SpeciesRepository`, `SessionRepository`, `PetRepository`, `RoomRepository`, `SaveFile`, `SpeciesLoader`, `GameStore`, `PlayerService`
- **ใช้ของใคร:** ไม่มี · ต้องเสร็จก่อน เพราะ B2, B3 ใช้ model และ GameStore · frontend ทุกคนใช้ DTO
- **ใครใช้ของเรา:** ทุกคน
- **branch:** `feat/b1-core-data`

## Backend

**Import ที่ต้องใช้ (รวมทุกไฟล์ของคุณ แต่ละไฟล์ใส่เฉพาะที่ใช้):**

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar
import json

from app.domain.enums import EggTier, Rarity, RoomStatus, SessionStatus
from app.domain.pet_policy import PetLevelPolicy
from app.dto import PetDTO, PlayerDTO, RoomDTO, SessionDTO, SpeciesDTO
from app.errors import AppError, InvalidStateError, NotFoundError, ValidationError
```

### `Settings`

- **ไฟล์:** `app/config.py`
- **ชนิด:** dataclass
- **inherit:** ไม่มี
- **สร้าง:** `Settings()`
- **หน้าที่:** ค่าตั้งค่ารวมไว้ที่เดียว ห้ามใส่ตัวเลขพวกนี้ลงในไฟล์อื่นตรง ๆ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `min_success_minutes` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `15` | อ่านขั้นต่ำกี่นาทีถึงได้ไข่ |
| `demo_speed` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1.0` | เร่งเวลาตอนเดโม 60.0 = 1 วินาทีจริงนับเป็น 1 นาที |
| `save_path` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"save.json"` | ไฟล์บันทึกข้อมูล |
| `species_seed_path` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `"seed/species.json"` | ไฟล์รายชื่อสัตว์ |
| `min_room_members` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `2` | สมาชิกห้องกลุ่มน้อยสุด |
| `max_room_members` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `6` | สมาชิกห้องกลุ่มมากสุด |

### `Clock`

- **ไฟล์:** `app/core/clock.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `Clock(speed=1.0)`
- **หน้าที่:** นาฬิกากลาง ทุกคนขอเวลาจากที่นี่ รองรับโหมดเร่งเวลา

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `speed` | `float` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1.0` | มาจาก Settings.demo_speed |

| method | return | ทำอะไร |
|---|---|---|
| `now()` | `datetime` | เวลาจริงตอนนี้ datetime.now(timezone.utc) |
| `elapsed_sec(started_at: datetime, until: datetime \| None = None)` | `int` | (until หรือ now − started_at) × speed ปัดลงเป็นวินาที |

### `Player`

- **ไฟล์:** `app/domain/player.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `Player(id, nickname, created_at)`
- **หน้าที่:** ผู้เล่นหนึ่งคน (ไม่มีรหัสผ่าน แค่ชื่อเล่น)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | player_id |
| `nickname` | `str` | ต้องส่งตอนสร้าง | ชื่อเล่น 1–20 ตัว ไม่ซ้ำ |
| `created_at` | `datetime` | ต้องส่งตอนสร้าง | วันสร้าง |

| method | return | ทำอะไร |
|---|---|---|
| `to_dto()` | `PlayerDTO` | แปลงเป็น PlayerDTO |
| `to_dict()` | `dict[str, Any]` | แปลงเป็น dict สำหรับเขียน JSON |
| `from_dict(data: dict[str, Any])` *@classmethod* | `Player` | สร้างจาก dict ที่อ่านจาก JSON |

### `Species`

- **ไฟล์:** `app/domain/species.py`
- **ชนิด:** dataclass (แก้ค่าไม่ได้)
- **inherit:** ไม่มี
- **สร้าง:** `Species(code=..., name=..., tier=..., rarity=..., sprite_path=...)`
- **หน้าที่:** สัตว์หนึ่งชนิด โหลดจาก species.json (ไม่ต้องบันทึกลง save)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `code` | `str` | ต้องส่งตอนสร้าง | รหัสไม่ซ้ำ |
| `name` | `str` | ต้องส่งตอนสร้าง | ชื่อ |
| `tier` | `EggTier` | ต้องส่งตอนสร้าง | ระดับไข่ |
| `rarity` | `Rarity` | ต้องส่งตอนสร้าง | ความหายาก |
| `sprite_path` | `str` | ต้องส่งตอนสร้าง | path รูป |
| `description` | `str` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `""` | คำอธิบาย |

| method | return | ทำอะไร |
|---|---|---|
| `to_dto()` | `SpeciesDTO` | แปลงเป็น SpeciesDTO |

### `StudySession`

- **ไฟล์:** `app/domain/study_session.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `StudySession(id, player_id, subject, started_at, room_id=None)`
- **หน้าที่:** การอ่านหนึ่งรอบของผู้เล่นหนึ่งคน · B1 สร้างตัวแปร + to_dict/from_dict · B3 เขียน method ที่เหลือ (เปลี่ยน status ผ่าน method เท่านั้น)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | session_id |
| `player_id` | `int` | ต้องส่งตอนสร้าง | ผู้เล่น |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `room_id` | `int \| None` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `None` | ห้องกลุ่ม ถ้าอ่านเดี่ยว = None |
| `status` | `SessionStatus` | สร้างใน `__init__` = `SessionStatus.RUNNING` | สถานะ |
| `ended_at` | `datetime \| None` | สร้างใน `__init__` = `None` | เวลาหยุด |
| `duration_sec` | `int` | สร้างใน `__init__` = `0` | เวลาที่อ่าน |
| `tier` | `EggTier \| None` | สร้างใน `__init__` = `None` | ไข่ที่ได้ |
| `species_code` | `str \| None` | สร้างใน `__init__` = `None` | สัตว์ที่ได้ |

| method | return | ทำอะไร |
|---|---|---|
| `stop(ended_at: datetime, duration_sec: int, min_success_sec: int)` | `SessionStatus` | บันทึกเวลา แล้วเปลี่ยนเป็น FAILED หรือ READY_TO_HATCH · ไม่ได้ RUNNING → InvalidStateError |
| `can_hatch()` | `bool` | True ถ้า READY_TO_HATCH |
| `mark_hatched(tier: EggTier, species_code: str)` | `None` | บันทึกไข่ + สัตว์ แล้วเปลี่ยนเป็น HATCHED · ไม่ได้ READY_TO_HATCH → InvalidStateError |
| `is_running()` | `bool` | True ถ้า RUNNING |
| `is_success()` | `bool` | True ถ้า HATCHED |
| `to_dto()` | `SessionDTO` | แปลงเป็น SessionDTO |
| `to_dict()` | `dict[str, Any]` | แปลงเป็น dict (datetime → ISO string, Enum → .value) |
| `from_dict(data: dict[str, Any])` *@classmethod* | `StudySession` | สร้างจาก dict |

### `OwnedPet`

- **ไฟล์:** `app/domain/owned_pet.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `OwnedPet(player_id, species_code, hatched_at, level=1, times_hatched=1)`
- **หน้าที่:** สัตว์ที่ผู้เล่นมี หนึ่งคนมีแต่ละชนิดได้ตัวเดียว ได้ซ้ำ = level up · B1 สร้างตัวแปร + to_dict/from_dict · B2 เขียน method ที่เหลือ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `player_id` | `int` | ต้องส่งตอนสร้าง | เจ้าของ |
| `species_code` | `str` | ต้องส่งตอนสร้าง | ชนิด |
| `hatched_at` | `datetime` | ต้องส่งตอนสร้าง | ได้ครั้งแรก |
| `level` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1` | level |
| `times_hatched` | `int` | ส่งหรือไม่ก็ได้ · ถ้าไม่ส่ง = `1` | ฟักได้กี่ครั้ง |

| method | return | ทำอะไร |
|---|---|---|
| `level_up(policy: PetLevelPolicy)` | `None` | times_hatched +1 และ level = policy.next_level(level) |
| `scale(policy: PetLevelPolicy)` | `float` | policy.scale_for(level) |
| `to_dto(species: Species, policy: PetLevelPolicy)` | `PetDTO` | แปลงเป็น PetDTO |
| `to_dict()` | `dict[str, Any]` | แปลงเป็น dict |
| `from_dict(data: dict[str, Any])` *@classmethod* | `OwnedPet` | สร้างจาก dict |

### `GroupRoom`

- **ไฟล์:** `app/domain/group_room.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `GroupRoom(id, subject, member_ids, session_ids, started_at)`
- **หน้าที่:** ห้องอ่านกลุ่ม · B1 สร้างตัวแปร + to_dict/from_dict · B3 เขียน method ที่เหลือ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `id` | `int` | ต้องส่งตอนสร้าง | room_id |
| `subject` | `str` | ต้องส่งตอนสร้าง | วิชา |
| `member_ids` | `list[int]` | ต้องส่งตอนสร้าง | player_id ของสมาชิก |
| `session_ids` | `list[int]` | ต้องส่งตอนสร้าง | session ของสมาชิก เรียงตาม member_ids |
| `started_at` | `datetime` | ต้องส่งตอนสร้าง | เวลาเริ่ม |
| `status` | `RoomStatus` | สร้างใน `__init__` = `RoomStatus.RUNNING` | สถานะ |
| `ended_at` | `datetime \| None` | สร้างใน `__init__` = `None` | เวลาหยุด |
| `duration_sec` | `int` | สร้างใน `__init__` = `0` | เวลาที่อ่าน |
| `tier` | `EggTier \| None` | สร้างใน `__init__` = `None` | ไข่ที่ทุกคนได้ |

| method | return | ทำอะไร |
|---|---|---|
| `stop(ended_at: datetime, duration_sec: int, min_success_sec: int)` | `RoomStatus` | บันทึกเวลา แล้วเปลี่ยนเป็น FAILED หรือ READY_TO_HATCH |
| `can_hatch()` | `bool` | True ถ้า READY_TO_HATCH |
| `mark_hatched(tier: EggTier)` | `None` | บันทึกระดับไข่ เปลี่ยนเป็น HATCHED |
| `to_dto(members: list[PlayerDTO])` | `RoomDTO` | แปลงเป็น RoomDTO |
| `to_dict()` | `dict[str, Any]` | แปลงเป็น dict |
| `from_dict(data: dict[str, Any])` *@classmethod* | `GroupRoom` | สร้างจาก dict |

### `BaseRepository`

- **ไฟล์:** `app/data/base_repository.py`
- **ชนิด:** abstract class
- **inherit:** `Generic[T]`
- **หน้าที่:** แม่ของที่เก็บข้อมูลทุกชนิด เก็บใน dict ใน memory และแปลงเป็น list ของ dict ไว้เขียนลง JSON (inheritance + generic)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `_items` | `dict[Any, T]` | สร้างใน `__init__` = `{}` | key → object |

| method | return | ทำอะไร |
|---|---|---|
| `key_of(item: T)` *abstract* | `Any` | key ของ object เช่น item.id |
| `item_from_dict(data: dict[str, Any])` *abstract* | `T` | สร้าง object จาก dict เช่น Player.from_dict(data) |
| `get(key: Any)` | `T` | หาตาม key ไม่เจอ → NotFoundError |
| `find(key: Any)` | `T \| None` | หาตาม key ไม่เจอคืน None |
| `add(item: T)` | `T` | เพิ่มหรือเขียนทับ แล้วคืน item |
| `list_all()` | `list[T]` | ทุกตัว |
| `next_id()` | `int` | id ถัดไป = max(key) + 1 (ว่างคืน 1) |
| `dump()` | `list[dict[str, Any]]` | ทุกตัวเป็น list ของ dict (เรียก to_dict) |
| `load(rows: list[dict[str, Any]])` | `None` | ล้างแล้วใส่ข้อมูลจาก JSON |

### `PlayerRepository`

- **ไฟล์:** `app/data/repositories.py`
- **ชนิด:** class
- **inherit:** `BaseRepository[Player]`
- **หน้าที่:** ผู้เล่น

| method | return | ทำอะไร |
|---|---|---|
| `key_of(item: Player)` | `int` | item.id |
| `item_from_dict(data: dict[str, Any])` | `Player` | Player.from_dict |
| `find_by_nickname(nickname: str)` | `Player \| None` | หาจากชื่อเล่น ไม่สนตัวพิมพ์เล็กใหญ่ |

### `SpeciesRepository`

- **ไฟล์:** `app/data/repositories.py`
- **ชนิด:** class
- **inherit:** `BaseRepository[Species]`
- **หน้าที่:** สัตว์ทุกชนิด (โหลดจาก seed ไม่บันทึก)

| method | return | ทำอะไร |
|---|---|---|
| `key_of(item: Species)` | `str` | item.code |
| `item_from_dict(data: dict[str, Any])` | `Species` | แปลง tier/rarity เป็น Enum |
| `list_by_tier(tier: EggTier)` | `list[Species]` | pool สำหรับสุ่มของไข่ระดับนี้ |

### `SessionRepository`

- **ไฟล์:** `app/data/repositories.py`
- **ชนิด:** class
- **inherit:** `BaseRepository[StudySession]`
- **หน้าที่:** การอ่านทุกรอบ

| method | return | ทำอะไร |
|---|---|---|
| `key_of(item: StudySession)` | `int` | item.id |
| `item_from_dict(data: dict[str, Any])` | `StudySession` | StudySession.from_dict |
| `get_running(player_id: int)` | `StudySession \| None` | รอบที่ RUNNING ของผู้เล่นนี้ (มีได้อันเดียว) |
| `list_by_player(player_id: int)` | `list[StudySession]` | ทุกรอบของผู้เล่น ใหม่สุดก่อน |

### `PetRepository`

- **ไฟล์:** `app/data/repositories.py`
- **ชนิด:** class
- **inherit:** `BaseRepository[OwnedPet]`
- **หน้าที่:** สัตว์ที่ผู้เล่นมี key = (player_id, species_code)

| method | return | ทำอะไร |
|---|---|---|
| `key_of(item: OwnedPet)` | `tuple[int, str]` | (item.player_id, item.species_code) |
| `item_from_dict(data: dict[str, Any])` | `OwnedPet` | OwnedPet.from_dict |
| `find_owned(player_id: int, species_code: str)` | `OwnedPet \| None` | ผู้เล่นมีตัวนี้หรือยัง |
| `list_by_player(player_id: int)` | `list[OwnedPet]` | สัตว์ทั้งหมดของผู้เล่น เรียงตามเวลาที่ได้ |

### `RoomRepository`

- **ไฟล์:** `app/data/repositories.py`
- **ชนิด:** class
- **inherit:** `BaseRepository[GroupRoom]`
- **หน้าที่:** ห้องอ่านกลุ่ม

| method | return | ทำอะไร |
|---|---|---|
| `key_of(item: GroupRoom)` | `int` | item.id |
| `item_from_dict(data: dict[str, Any])` | `GroupRoom` | GroupRoom.from_dict |

### `SaveFile`

- **ไฟล์:** `app/data/save_file.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `SaveFile(path)`
- **หน้าที่:** อ่านและเขียนไฟล์ save.json (เขียนลงไฟล์ชั่วคราวก่อนแล้วค่อยเปลี่ยนชื่อ กันไฟล์พังตอนปิดแอปกลางคัน)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `path` | `Path` | ต้องส่งตอนสร้าง | มาจาก Settings.save_path |

| method | return | ทำอะไร |
|---|---|---|
| `exists()` | `bool` | มีไฟล์หรือยัง |
| `read()` | `dict[str, Any]` | อ่าน JSON ไม่มีไฟล์คืน {} · ไฟล์พัง → AppError |
| `write(data: dict[str, Any])` | `None` | เขียน JSON (ensure_ascii=False, indent=2) |

### `SpeciesLoader`

- **ไฟล์:** `app/data/species_loader.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `SpeciesLoader(path)`
- **หน้าที่:** อ่าน seed/species.json แล้วคืน list ของ Species

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `path` | `Path` | ต้องส่งตอนสร้าง | มาจาก Settings.species_seed_path |

| method | return | ทำอะไร |
|---|---|---|
| `load()` | `list[Species]` | อ่านไฟล์ แปลง tier/rarity เป็น Enum · ผิดรูปแบบ → AppError |

### `GameStore`

- **ไฟล์:** `app/data/game_store.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `GameStore(save_file)`
- **หน้าที่:** รวมที่เก็บข้อมูลทุกชนิด service ทุกตัวรับ GameStore · service ที่แก้ข้อมูลต้องเรียก save() ท้าย method เสมอ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `save_file` | `SaveFile` | ต้องส่งตอนสร้าง | ไฟล์ save |
| `players` | `PlayerRepository` | สร้างใน `__init__` = `PlayerRepository()` | ผู้เล่นทั้งหมด |
| `species` | `SpeciesRepository` | สร้างใน `__init__` = `SpeciesRepository()` | repository สัตว์ทุกชนิด |
| `sessions` | `SessionRepository` | สร้างใน `__init__` = `SessionRepository()` | repository การอ่าน |
| `pets` | `PetRepository` | สร้างใน `__init__` = `PetRepository()` | repository สัตว์ที่มี |
| `rooms` | `RoomRepository` | สร้างใน `__init__` = `RoomRepository()` | repository ห้องกลุ่ม |

| method | return | ทำอะไร |
|---|---|---|
| `open(settings: Settings)` *@classmethod* | `GameStore` | สร้าง GameStore โหลดสัตว์จาก SpeciesLoader แล้วเรียก load() |
| `load()` | `None` | อ่าน save.json ใส่ players, sessions, pets, rooms |
| `save()` | `None` | เขียน players, sessions, pets, rooms ลง save.json |

### `PlayerService`

- **ไฟล์:** `app/services/player_service.py`
- **ชนิด:** class
- **inherit:** ไม่มี
- **สร้าง:** `PlayerService(store, clock)`
- **หน้าที่:** สร้าง/เลือกผู้เล่น (ใช้ในหน้า Landing และหน้าเลือกสมาชิกห้องกลุ่ม)

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
|---|---|---|---|
| `store` | `GameStore` | ต้องส่งตอนสร้าง | ที่เก็บข้อมูลกลาง |
| `clock` | `Clock` | ต้องส่งตอนสร้าง | นาฬิกากลาง |

| method | return | ทำอะไร |
|---|---|---|
| `list_players()` | `list[PlayerDTO]` | ผู้เล่นทุกคน เรียงตามชื่อ |
| `create_player(nickname: str)` | `PlayerDTO` | ตัดช่องว่าง · ว่าง/ยาวเกิน 20/ซ้ำ → ValidationError(field="nickname") · save() |
| `get_player(player_id: int)` | `PlayerDTO` | ไม่เจอ → NotFoundError |

## เช็กลิสต์ก่อนส่ง PR

- [ ] GameStore.save() แล้ว load() ใหม่ ข้อมูลต้องเหมือนเดิม
- [ ] to_dict/from_dict ของทุก model แปลงไปกลับแล้วค่าเท่าเดิม
- [ ] PlayerService.create_player ชื่อซ้ำ/ว่าง ต้อง ValidationError
- [ ] Clock.elapsed_sec กับ speed = 60 ได้ค่าถูก
- [ ] ชื่อ class, ตัวแปร, method, parameter ตรงกับเอกสารนี้ทุกตัว
- [ ] ไม่มี `print`, ไม่มีบรรทัด comment, มี type hint ครบ
