# CPE Egg Hatch · Phase 1 Feature Flowchart

เป้าหมาย D5: เล่นได้ครบหนึ่งรอบ (playable end-to-end MVP) ตั้งแต่เปิดแอปจนได้สัตว์กลับมาอยู่ในห้องภาค

## ขอบเขต Phase 1

| มีใน Phase 1 | ยังไม่มี (ไป Phase 2–3) |
|---|---|
| 4 หน้า: Landing → Lobby → Focus → Hatch/Result | Login / Signup / Google OAuth |
| นาฬิกานับขึ้น + ปลดล็อกไข่ 3 ระดับ (15 / 30 / 60 นาที) | แชท CPEGO แบบกล่องแชท |
| CPEGO เป็น popup/bubble เด้งตอนครบ milestone | Database (Phase 2) |
| สุ่มสัตว์ตาม rarity ของไข่ | CPE Dex, History, Analytics (Phase 3) |
| สัตว์ที่ได้ไปเดินใน Lobby (ตัวซ้ำ = level +1) | Advanced Sanctuary (Phase 3) |
| เก็บข้อมูลใน memory (ปิดแอปแล้วหาย) | |

## Flowchart ทั้งเกม

```mermaid
flowchart TD
  START(["เปิดแอป"]) --> L

  subgraph P1["① Landing"]
    L["โลโก้ + ชื่อเกม"] --> L1["กด START"]
  end

  L1 --> LB

  subgraph P2["② Lobby · ห้องภาคคอม"]
    LB["โชว์ห้องภาค<br/>สัตว์ที่ฟักได้เดินไปมา"]
    LB --> LB0{"มีสัตว์แล้วหรือยัง?"}
    LB0 -- "ยังไม่มี" --> LB1["ห้องว่าง + ข้อความชวนเริ่มอ่าน"]
    LB0 -- "มีแล้ว" --> LB2["วาดสัตว์ตาม level<br/>level สูง = ตัวใหญ่ขึ้น"]
    LB1 --> LBA
    LB2 --> LBA
    LBA{"ผู้ใช้กดอะไร"}
    LBA -- "HOW TO" --> HT["popup How to Play"] --> LBA
    LBA -- "START FOCUS" --> SP["popup ตั้งค่า<br/>ใส่ชื่อวิชา + ดู Egg Rate"]
    SP --> SP1{"ใส่ชื่อวิชาแล้ว?"}
    SP1 -- "ยัง" --> SP2["เตือนให้ใส่ชื่อวิชา"] --> SP
    SP1 -- "BACK" --> LBA
  end

  SP1 -- "START" --> F

  subgraph P3["③ Focus · ฟักไข่"]
    F["นาฬิกาเริ่มนับขึ้น 00:00<br/>ไข่อยู่กลางจอ"]
    F --> FT["ทุก 1 วินาที อัปเดตเวลา"]
    FT --> FM{"ครบ 15 / 30 / 60 นาที?"}
    FM -- "ครบ" --> FB["CPEGO bubble เด้ง<br/>บอกว่าปลดล็อกไข่ระดับไหน<br/>ไข่เปลี่ยนรูปตามระดับ"] --> FT
    FM -- "ยัง" --> FT
    FT -.->|"กด STOP"| FS{"Are you sure to stop?"}
    FS -- "NO" --> FT
    FS -- "YES" --> FC{"เวลารวม ≥ 15 นาที?"}
    FC -- "ใช่" --> FE["popup Choose an egg<br/>ไข่ที่ยังไม่ปลดล็อกเป็นสีเทา"]
    FE --> FE1{"ยืนยันเลือกไข่นี้?"}
    FE1 -- "NO" --> FE
  end

  FC -- "ไม่ถึง" --> RF
  FE1 -- "YES" --> H

  subgraph P4["④ Hatch / Result"]
    H["สุ่ม rarity ตามน้ำหนักของไข่<br/>แล้วสุ่มสัตว์ใน rarity นั้น"]
    H --> HA["Animation: ไข่สั่น → แตก → TADA"]
    HA --> HN{"เคยมีตัวนี้แล้ว?"}
    HN -- "ยังไม่มี" --> HN1["เพิ่มเข้าห้องภาค level 1"]
    HN -- "มีแล้ว" --> HN2["level +1 ตัวใหญ่ขึ้น"]
    HN1 --> RS
    HN2 --> RS
    RS["Congrats! You got ...<br/>ชื่อสัตว์ + rarity + วิชา + เวลาที่อ่าน"]
    RF["ไข่ยังไม่ฟัก<br/>วิชา + เวลาที่อ่าน + ต้องอ่านอีกกี่นาที"]
  end

  RS -- "RETURN TO LOBBY" --> LB
  RF -- "RETURN TO LOBBY" --> LB
```

## ลำดับหน้า (สรุป)

```mermaid
flowchart LR
  A["① Landing"] -- "START" --> B["② Lobby"]
  B -- "START FOCUS + ใส่วิชา" --> C["③ Focus"]
  C -- "STOP ≥ 15 นาที + เลือกไข่" --> D["④ Hatch / Result<br/>สำเร็จ"]
  C -- "STOP < 15 นาที" --> E["④ Result<br/>ไม่สำเร็จ"]
  D -- "RETURN TO LOBBY" --> B
  E -- "RETURN TO LOBBY" --> B
```

## Feature ของแต่ละหน้า

### ① Landing
- โลโก้ + ชื่อเกม
- ปุ่ม `START` ไป Lobby

### ② Lobby
- ห้องภาคพร้อมสัตว์ที่ฟักได้ในรอบการเล่นนี้ เดินสุ่มไปมาแบบง่าย ขนาดตาม level
- ปุ่ม `HOW TO` เปิด popup อธิบายวิธีเล่น
- ปุ่ม `START FOCUS` เปิด popup ใส่ชื่อวิชา + ดู Egg Rate แล้วกด `START` ไปหน้า Focus

### ③ Focus
- นาฬิกานับขึ้น (นาที:วินาที)
- รูปไข่เปลี่ยนตามระดับที่ปลดล็อก
- CPEGO bubble เด้งตอนครบ 15 / 30 / 60 นาที แล้วหายเอง
- ปุ่ม `STOP` → popup ยืนยัน → ถ้าถึง 15 นาทีเปิด popup `Choose an egg` + ยืนยัน

### ④ Hatch / Result
- สุ่มสัตว์ + animation ฟักไข่
- ได้ตัวใหม่ → เพิ่มเข้าห้องภาค · ได้ตัวซ้ำ → level +1
- สรุปผล: สัตว์ที่ได้, วิชา, เวลาที่อ่าน
- ถ้าไม่ถึง 15 นาที โชว์หน้าไม่สำเร็จแทน
- ปุ่ม `RETURN TO LOBBY`

## กติกาเกม Phase 1

| ไข่ | เวลาขั้นต่ำ | Common | Rare | Epic | Legendary |
|---|---|---|---|---|---|
| ไข่รุ่นเรา | 15 นาที | 70% | 25% | 5% | 0% |
| ไข่รุ่นพี่ | 30 นาที | 40% | 40% | 17% | 3% |
| ไข่อาจารย์ | 60 นาที | 10% | 40% | 35% | 15% |

## สิ่งที่ตัดสินใจแทนไว้ (แก้ได้)

- หน้า Set up เดิมย่อเป็น popup ใน Lobby และหน้า Summary เดิมย่อเป็น popup `Choose an egg` ในหน้า Focus จะได้เหลือ 4 หน้าตามแผน
- ไม่มี database ข้อมูลทั้งหมด (สัตว์ในห้องภาค, รอบที่กำลังอ่าน) อยู่ใน object เดียวใน memory ปิดแอปแล้วเริ่มใหม่ Phase 2 ค่อยเปลี่ยนไปบันทึกลง database
- ตอนเดโมควรมีโหมดเร่งเวลา (เช่น 1 วินาที = 1 นาที) ไม่ต้องนั่งรอ 15 นาทีจริง
