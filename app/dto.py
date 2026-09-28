from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar
import json

class PlayerDTO:
    def __init__(self, id, nickname):
        self.id = id
        self.nickname = nickname 
    def __str__(self):
        return f"id : {self.id}, nickname : {self.nickname}"