from __future__ import annotations
from ..dto import SpeciesDTO
from app.domain.enums import EggTier,Rarity
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar
import json


class Species:
    def __init__(self, code:str, name:str, tier: EggTier, rarity: Rarity, sprite_path : str, description :str = ""):
        self.code = code
        self.name = name
        self.tier = tier
        self.rarity = rarity
        self.sprite_path = sprite_path
        self.description = description
        
    def to_dto(self):
        return SpeciesDTO()
    
        