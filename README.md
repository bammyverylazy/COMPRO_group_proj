# CPE Egg Hatch

แอปพลิเคชันด้านการโฟกัสและฟักไข่แบบเบา ๆ ที่ผู้ใช้เริ่ม session การเรียน/ทำงาน, บันทึก task note, ให้ timer ทำงานต่อไป, หยุดเมื่อพร้อม, รีวิว Session Summary ที่จำเป็น, ปลดล็อก tier ของไข่, และฟักสัตว์เป็นรางวัลจากการโฟกัส

## ทิศทางของสินค้า

โปรเจ็กต์นี้มีเป้าหมายเพื่อเป็น MVP แบบไม่มีการยืนยันตัวตน (no-auth) โดย Phase 1 จะเน้นเฉพาะลูปหลักเท่านั้น:

- Landing / Start
- Lobby
- Start Focus
- Task note entry
- Timer
- Stop
- Session Summary
- Egg unlock + selection
- Hatch + result
- Return to lobby

Checkpoint MVP ที่ต้องตรงตามคือ:

START → LOBBY → START FOCUS → TASK NOTE → TIMER → STOP → SESSION SUMMARY → EGG UNLOCK → EGG SELECTION → HATCH → RESULT → LOBBY

## สิ่งที่ไม่อยู่ใน Phase 1

โปรเจ็กต์นี้ตั้งใจให้ไม่รวมสิ่งต่อไปนี้ไว้ใน MVP:

- Login / sign up
- Google OAuth
- Password / remember-me flow
- Subject หรือ course selection
- ประวัติแชทหรือการส่งข้อความ
- Dex, analytics, และ sanctuary expansion ในฐานะ feature หลักของ MVP
- Database เป็น blocker สำหรับ Phase 1

## ลูปหลักและกฎการทำงาน

1. Session การโฟกัสเริ่มจาก task note
2. Timer จะนับเวลาที่ผ่านไป
3. ผู้ใช้จะหยุด session เพื่อประเมินผลลัพธ์
4. Session Summary จำเป็นต้องทำก่อน hatch
5. การปลดล็อกไข่ใช้เกณฑ์เวลาเดิมที่มีอยู่ในโปรเจกต์
6. ไข่ที่เลือกจะถูกใช้ในการฟักสัตว์
7. CPEGO เป็น notification bubble แบบ milestone ไม่ใช่ระบบแชทแบบ real-time

## โจทย์เวลาต่ำสุดที่ต้องรักษา

ตรรกะเรื่องเวลา minimum ที่มีอยู่เดิมจะถูกเก็บไว้และยังเป็นเส้นทางปลดล็อกหลัก:

- Freshman egg: 15 นาที
- Senior egg: 30 นาที
- Professor egg: 60 นาที

ตรรกะนี้เป็นพื้นฐานของ progression ในเกม reward loop

## แผนการพัฒนา

### Phase 1

- Landing / lobby
- Flow ของ focus session
- การบันทึก task note
- Timer + stop logic
- Requirement สำหรับ Session Summary
- Egg unlock + selection
- Hatch result
- CPEGO milestone bubble notifications

### Phase 2

- Persistent storage และ session history
- Owned creature collection
- Save/load state ระหว่าง session
- การกู้คืน session และ replay ที่ดีขึ้น

### Phase 3

- Sanctuary / collection views ขั้นสูง
- Dex และ analytics
- Expanded progression และ visual polish
- Optional auth และ profile systems เฉพาะหลังจาก MVP เสถียรแล้ว

## สถาปัตยกรรมหลัก

โปรเจ็กต์ควรทำตามโครงสร้างแบบชั้นง่าย ๆ:

- UI layer: screens และ widgets
- Service layer: session, summary, hatch, และ tier logic
- Domain layer: enums, egg rules, และ reward logic
- Persistence layer: เป็นทางเลือกในภายหลัง ไม่ใช่ dependency ของ Phase 1

การออกแบบที่แนะนำคือใช้ DTO-based service response และหลีกเลี่ยงให้ UI import repository หรือ model โดยตรง

## สรุป domain model

### `EggTier`

- `FRESHMAN` = ไข่ 15 นาที
- `SENIOR` = ไข่ 30 นาที
- `PROFESSOR` = ไข่ 60 นาที

### `Rarity`

- `COMMON`
- `RARE`
- `EPIC`
- `LEGENDARY`

### `SessionStatus`

- `IDLE`
- `RUNNING`
- `STOPPED`
- `SUMMARY`
- `READY_TO_HATCH`
- `FAILED`
- `HATCHED`

### `StudySession`

ข้อมูลหลักของ focus session ควรมีอย่างน้อย:

- `id`
- `task_note`
- `started_at`
- `ended_at`
- `duration_sec`
- `status`
- `chosen_tier`
- `species_id`
- `unlocked_tier`

Method ที่ควรมี:

- `elapsed_sec(now)`
- `start(task_note)`
- `stop(now, min_success_sec)`
- `can_hatch()`
- `mark_hatched(tier, species_id)`
- `is_success()`
- `to_dto()`

### `SummaryDTO`

ใช้หลังจาก stop flow และควรมีข้อมูลต่อไปนี้:

- `session_id`
- `task_note`
- `duration_sec`
- `status`
- `unlocked_tiers`
- `best_tier`

### `FocusSessionService`

หน้าที่หลัก:

- เริ่ม session ใหม่
- ดึง session ที่กำลังทำอยู่
- วัด elapsed time
- หยุด session
- กำหนด unlock state จากระยะเวลา
- คืนผลลัพธ์ที่ UI ของ summary จำเป็นต้องใช้

### `SummaryService`

หน้าที่หลัก:

- ตรวจสอบว่า session นั้นสามารถเข้าสู่ summary ได้หรือไม่
- ส่งข้อมูล summary ให้ UI
- เปิดเผย egg tiers ที่ unlock ได้

### `HatchService`

หน้าที่หลัก:

- ตรวจสอบ session และ egg ที่เลือก
- สุ่ม species จาก egg tier pool
- สร้างหรืออัปเกรด owned creature
- ทำเครื่องหมายว่า session นี้ hatching แล้ว
- คืน hatch result DTO

### `CPEGO`

CPEGO ควรเป็น notification bubble แบบ milestone และทำหน้าที่เป็น UI assistant แบบเบา ๆ แทนการเป็น chat interface โดยควรแสดง notification เช่น:

- session started
- milestone reached at 15 minutes
- milestone reached at 30 minutes
- milestone reached at 60 minutes
- egg unlocked หรือ hatch complete

## ข้อจำกัดด้านการ implement

- ใช้ enum comparison แบบ `is` แทน string comparison
- ให้ UI และ service contract อยู่ในรูป DTO-based
- ถือว่า database persistence เป็นเรื่อง Phase 2 เว้นแต่ทีมจะเลือกใช้ local storage ในภายหลัง
- ให้ MVP คงความเล็กและเรียบ และหลีกเลี่ยง auth, subject, หรือ chat จนกว่าลูปหลักจะเสถียรแล้ว
- รักษา threshold logic เดิมไว้: 15 / 30 / 60 นาที
- ให้ `Session Summary` เป็นขั้นตอนที่จำเป็นก่อน hatch

## รายการใน future scope

ฟีเจอร์เหล่านี้เป็นไอเดียที่ใช้ได้ใน phase ถัดไป แต่ไม่ควรเป็นส่วนหนึ่งของ Phase 1 acceptance:

- authentication และ profile management
- Google OAuth
- course และ subject models
- CPEGO chat transcript/history
- dex analytics dashboards
- advanced sanctuary management
- full database-backed persistence

## สรุป

MVP นี้ไม่ใช่ study tracker แบบ auth-heavy แต่เป็น product loop ที่มุ่งเน้นเรื่องเดียว: เริ่มงาน, โฟกัสต่อเนื่อง, หยุด, สรุป, ปลดล็อกไข่, และฟักผลลัพธ์ นี่คือคำจำกัดความของผลิตภัณฑ์ที่ codebase และเอกสารควรสะท้อนให้เห็น

## `Egg`

แม่ของไข่ทุกระดับ

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
| --- | --- | --- | --- |
| `tier` | `EggTier` | ภายใน class | ระดับไข่ |
| `name_th` | `str` | ภายใน class | ชื่อภาษาไทย |
| `image_path` | `str` | ภายใน class | รูปไข่ |

| method | คืนค่า | หน้าที่ |
| --- | --- | --- | --- |
| `required_minutes()` *abstract* | `int` | เวลาขั้นต่ำ |
| `rarity_weights()` *abstract* | `dict[Rarity, int]` | น้ำหนักสุ่มสัตว์ |
| `is_unlocked(duration_sec: int)` | `bool` | True ถ้าเวลาเพียงพอ |
| `roll(pool: list[Species], gacha: GachaMachine)` | `Species` | เลือกสัตว์จาก pool ตาม rarity |
| `to_tier_info()` | `TierInfo` | แปลงเป็น DTO |

### `FreshmanEgg` / `SeniorEgg` / `ProfessorEgg`

*class* · สืบทอดจาก `Egg`

Implement เหมือนเดิมแต่ใช้โครงใหม่กับ Phase 1

### `EggFactory`

*class* · `app/domain/egg_factory.py`

**สร้าง:** `EggFactory()`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
| --- | --- | --- | --- |
| `_registry` | `dict[EggTier, type[Egg]]` | สร้างใน `__init__` | mapping tier → egg class |

| method | คืนค่า | หน้าที่ |
| --- | --- | --- | --- |
| `create(tier: EggTier)` | `Egg` | สร้างไข่ตาม tier |
| `all()` | `list[Egg]` | คืน egg ทั้งหมด เรียงจากต่ำไปสูง |
| `unlocked_for(duration_sec: int)` | `list[Egg]` | ตัวที่ unlock จากเวลา |
| `best_for(duration_sec: int)` | `Egg | None` | tier สูงสุดที่ unlock |

### `TierService`

*class* · `app/services/tier_service.py`

**สร้าง:** `TierService(factory=None)`

| ตัวแปร | ชนิด | สร้างยังไง | ความหมาย |
| --- | --- | --- | --- |
| `factory` | `EggFactory | None` | ส่งหรือไม่ก็ได้ | ถ้า None ให้สร้างเอง |

| method | คืนค่า | หน้าที่ |
| --- | --- | --- | --- |


