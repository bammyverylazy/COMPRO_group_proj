# CPE Egg Hatch Class Spec

เอกสารนี้กำหนดสถาปัตยกรรมขั้นต่ำที่จำเป็นสำหรับ MVP และสอดคล้องกับทิศทางของสินค้าใน README: ไม่มี auth, ไม่มี course selection, ไม่มี chat, มี Session Summary ที่จำเป็น, และมีลูปโฟกัสที่จบที่การฟักไข่

## 1. ขอบเขตและข้อจำกัดของสินค้า

Phase 1 ถูกออกแบบให้จำกัดและไม่กว้างเกินไป การทำงานของโปรเจ็กต์ต้องไม่ถือว่า login, OAuth, subject selection, หรือ chat เป็น requirement หลัก

Flow ที่ต้องมีใน Phase 1:

START → LOBBY → START FOCUS → TASK NOTE → TIMER → STOP → SESSION SUMMARY → EGG UNLOCK → EGG SELECTION → HATCH → RESULT → LOBBY

### สิ่งที่อยู่ใน scope ของ Phase 1

- Landing / lobby
- Focus session
- การบันทึก task note
- Timer และ stop logic
- Session Summary ที่จำเป็น
- Egg unlock และ selection
- Hatch result
- CPEGO milestone notifications

### สิ่งที่อยู่นอก scope ของ Phase 1

- Login / sign up
- Google OAuth
- Remember-me
- Subject / course model
- Chat history
- Dex / analytics / sanctuary expansion ในฐานะ MVP หลัก
- Database เป็น blocker สำหรับ flow เริ่มต้น

## 2. กฎการตั้งชื่อและสถาปัตยกรรม

### การตั้งชื่อ

- Classes: PascalCase
- Methods และ variables: snake_case
- Constants: UPPER_SNAKE
- Private members: ใช้ underscore นำหน้า
- Boolean names: ใช้ `is_`, `has_`, หรือ `can_`
- Time fields: ลงท้ายด้วย `_at`
- Duration fields: ลงท้ายด้วย `_sec`
- ID fields: ลงท้ายด้วย `_id`
- Collection: ใช้ชื่อพหูพจน์

### กฎสถาปัตยกรรม

- UI code ต้องไม่ import repositories หรือ models โดยตรง
- Service ควรกลับ DTO แทน domain model
- ใช้ enum comparison แบบ `is` แทน string comparison
- ใช้ `utcnow()` สำหรับ timestamp
- ถ้ามี method ใดที่ยังไม่ implement ใน MVP ให้ raise `NotImplementedError`
- ใช้ `AppError` และ subclass สำหรับ validation, state, และปัญหาข้อมูล

## 3. Phase map

| Feature | Phase |
| --- | --- |
| Lobby, focus flow, summary, hatch flow | Phase 1 |
| Timer + egg unlock logic | Phase 1 |
| CPEGO bubble notifications | Phase 1 |
| Database persistence และ session history | Phase 2 |
| Owned creature collection | Phase 2 |
| Dex, analytics, advanced sanctuary | Phase 3 |
| Auth / OAuth | Phase 3 |

## 4. Enum หลักและ error

### `EggTier`

Enum ใน `app/domain/enums.py`

| Value | Meaning |
| --- | --- |
| `FRESHMAN` | ไข่ 15 นาที |
| `SENIOR` | ไข่ 30 นาที |
| `PROFESSOR` | ไข่ 60 นาที |

### `Rarity`

Enum ใน `app/domain/enums.py`

| Value | Meaning |
| --- | --- |
| `COMMON` | reward ธรรมดา |
| `RARE` | reward น่าจะมีค่า |
| `EPIC` | reward หายาก |
| `LEGENDARY` | reward สูงสุด |

### `SessionStatus`

Enum ใน `app/domain/enums.py`

| Value | Meaning |
| --- | --- |
| `IDLE` | session ยังไม่เริ่ม |
| `RUNNING` | session กำลังทำงาน |
| `STOPPED` | session หยุดแล้ว |
| `SUMMARY` | เข้าสู่ summary แล้ว |
| `READY_TO_HATCH` | ผ่านเกณฑ์ unlock และพร้อมเลือกไข่ |
| `FAILED` | เวลารวมต่ำกว่าขั้นต่ำ |
| `HATCHED` | ฟักสำเร็จแล้ว |

> `ABANDONED` อาจมีในอนาคตเป็น optional state แต่ไม่ควรใช้เป็น requirement หลักของ Phase 1

### `AppError`

Base exception ใน `app/errors.py`

Fields:
- `message: str`
- `field: str | None = None`

### `ValidationError`

Subclass ของ `AppError` สำหรับ task note ที่ invalid หรือค่าที่ไม่ถูกต้อง

### `NotFoundError`

Subclass ของ `AppError` สำหรับ session หรือ species ที่ไม่พบ

### `InvalidStateError`

Subclass ของ `AppError` ที่เกิดเมื่อ user ทำต่อขั้นตอนไม่ถูกลำดับ เช่น พยายาม hatch ก่อนจะถึง summary หรือก่อนถึง unlock criteria

## 5. Domain model

### `StudySession`

Domain model หลักสำหรับ single focus session

File: `app/models/study_session.py`

Fields ที่ต้องมี:
- `id: int`
- `task_note: str | None`
- `started_at: datetime`
- `ended_at: datetime | None`
- `duration_sec: int`
- `status: SessionStatus`
- `unlocked_tier: EggTier | None`
- `chosen_tier: EggTier | None`
- `species_id: int | None`

Methods ที่ต้องมี:
- `elapsed_sec(now: datetime) -> int`
- `start(task_note: str | None) -> None`
- `stop(now: datetime, min_success_sec: int) -> SessionStatus`
- `can_hatch() -> bool`
- `mark_hatched(tier: EggTier, species_id: int) -> None`
- `is_success() -> bool`
- `to_dto() -> SessionDTO`

### `SessionDTO`

Data object ที่ส่งกลับให้ UI

Fields:
- `id: int`
- `task_note: str | None`
- `started_at: datetime`
- `duration_sec: int`
- `status: SessionStatus`
- `unlocked_tier: EggTier | None = None`

### `StopResult`

Fields:
- `session_id: int`
- `status: SessionStatus`
- `duration_sec: int`
- `unlocked_tiers: list[EggTier]`

### `SummaryDTO`

Fields:
- `session_id: int`
- `task_note: str | None`
- `duration_sec: int`
- `status: SessionStatus`
- `unlocked_tiers: list[EggTier]`
- `best_tier: EggTier | None`

## 6. Egg logic

### `Egg`

Abstract base class ใน `app/domain/eggs.py`

Members ที่ต้องมี:
- `tier: EggTier`
- `name_th: str`
- `image_path: str`

Methods ที่ต้องมี:
- `required_minutes() -> int`
- `rarity_weights() -> dict[Rarity, int]`
- `is_unlocked(duration_sec: int) -> bool`
- `roll(pool: list[Species], gacha: GachaMachine) -> Species`
- `to_tier_info() -> TierInfo`

### ไข่แต่ละระดับ

- `FreshmanEgg` = 15 นาที
- `SeniorEgg` = 30 นาที
- `ProfessorEgg` = 60 นาที

### `EggFactory`

File: `app/domain/egg_factory.py`

Responsibility:
- สร้าง egg instances ตาม tier
- คืนค่ารายการ egg ทั้งหมดเรียงจากต่ำไปสูง
- กำหนดว่า egg ใด unlock เมื่อเวลาผ่านไปเท่าไร
- คำนวณ best unlocked tier

### `TierInfo`

Fields:
- `tier: EggTier`
- `name_th: str`
- `required_minutes: int`
- `rarity_weights: dict[Rarity, int]`

### `TierService`

File: `app/services/tier_service.py`

Method:
- `list_tiers() -> list[TierInfo]`

## 7. Service หลักสำหรับลูป core

### `FocusSessionService`

File: `app/services/focus_service.py`

Responsibility:
- สร้าง focus session ใหม่
- ตรวจสอบค่า task note
- ดึง session ที่ยังกำลังทำอยู่
- คำนวณ elapsed seconds
- หยุด session และตัดสินว่าเป็น `FAILED` หรือ `READY_TO_HATCH`
- คืนค่า result ที่ `SummaryView` ต้องใช้

Method ที่ต้องใช้:
- `start(task_note: str | None) -> SessionDTO`
- `get_running() -> SessionDTO | None`
- `elapsed(session_id: int) -> int`
- `stop(session_id: int) -> StopResult`

### `SummaryService`

File: `app/services/summary_service.py`

Responsibility:
- ตรวจว่า session นั้นสามารถเข้าสู่ summary ได้หรือไม่
- สร้าง summary data
- เปิดเผย egg tiers ที่ unlock ได้และ best unlockable tier

Method:
- `get_summary(session_id: int) -> SummaryDTO`

### `HatchService`

File: `app/services/hatch_service.py`

Responsibility:
- ตรวจสอบ session และ egg tier ที่เลือก
- เลือก species ตาม rarity weights ของ tier
- สร้างหรืออัปเดต owned creature
- ทำเครื่องหมายว่าครั้งนี้ hatching แล้ว
- คืนค่า final result DTO

Method:
- `hatch(session_id: int, tier: EggTier) -> HatchResult`

## 8. CPEGO notification bubble

CPEGO ไม่ควรถูก model เป็น chat feature แต่เป็น notification mechanism สำหรับ milestone เล็ก ๆ

### `CpegoMessage`

Fields:
- `text: str`
- `kind: str = "info"`
- `created_at: datetime = utcnow()`

### `CpegoBubble`

UI component สำหรับข้อความ milestone

Responsibility:
- เก็บ notification list ที่เล็ก
- แสดง unread count เมื่อนำ milestone ใหม่เข้ามา
- เปิดหรือปิด bubble panel แบบกะทัดรัด
- แสดงข้อความ milestone เช่น "15-minute egg unlocked" หรือ "session summary ready"

วัตถุนี้แทน model ของ chat panel เก่า และสอดคล้องกับ requirement ของ MVP ที่ว่า CPEGO เป็น notification assistant ไม่ใช่ interface สื่อสารแบบ live conversation

## 9. Flow ของ UI

### `LobbyView`

หน้าหลักของแอป ควรมี:
- start focus button
- optional how-to view
- navigation ไป summary/history ถ้ามีในภายหลัง

### `FocusView`

หน้าจอโฟกัส มี:
- task note input หรือแสดงข้อมูล
- timer
- indicator สถานะ egg ที่ lock/unlock
- CPEGO bubble
- stop button

### `SummaryView`

หน้า Session Summary มี:
- total session time
- best unlocked tier
- egg selection list
- confirmation flow ก่อน hatch

### `HatchView`

หน้าแสดงผลลัพธ์ มี:
- hatching animation
- creature reveal
- action กลับไป lobby

## 10. Phase 2 และ future scope

Phase 2 สามารถเพิ่มได้:
- persistent database tables
- session history
- owned creature collection persistence
- user-based saves

Future scope ยังคงอยู่นอก MVP อย่างชัดเจน:
- authentication และ OAuth
- chat history และ messaging
- course selection support
- advanced analytics และ dex expansion

## 11. นิยามสั้น ๆ ของ MVP

MVP ถูกกำหนดเป็น loop ที่ไม่มี auth เดียว:

1. เริ่ม focus session
2. บันทึก task note
3. run timer
4. หยุด session
5. ดู required summary
6. ปลดล็อกไข่ตาม logic 15 / 30 / 60 นาที
7. เลือกไข่
8. ฟักผลลัพธ์
9. กลับสู่ lobby

นี่คือพฤติกรรมของผลิตภัณฑ์ที่ repository ควรเอกสารและ implement ให้ตรงตาม