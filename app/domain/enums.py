from __future__ import annotations

from enum import Enum


# ไม่แน่ใจเป็นของใคร เค้าร่างไว้เพราะมันเกี่ยวกับโค้ด B1 พอดี สามารถแก้ต่อได้เลย
class EggTier(Enum):
    FRESHMAN = "freshman"
    SENIOR ="senior"
    PROFESSOR = "professor"
    
class Rarity(Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    
class SessionStatus(Enum):
    RUNNING = "running"
    READY_TO_HATCH = "ready_to_hatch"
    HATCHED = "hatched"
    FAILED = "failed"
    
class RoomStatus(Enum):
    RUNNING = "running"
    READY_TO_HATCH = "ready_to_hatch"
    HATCHED = "hatched"
    FAILED = "failed"
