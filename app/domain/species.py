from __future__ import annotations
from ..services.dto import SpeciesDTO
from .enums import EggTier,Rarity
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar
import json

@dataclass(frozen=True)
class Species:
    code:str
    name:str
    tier: EggTier
    rarity: Rarity
    sprite_path : str
    description :str = ""
        
    def to_dto(self):
        return SpeciesDTO(
        code = self.code,
        name = self.name ,
        tier = self.tier ,
        rarity = self.rarity,
        sprite_path= self.sprite_path,
        description= self.description)
    
        