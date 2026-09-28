from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar
import json

class Clock:
    def __init__(self, speed = 1.0):
        self.speed = speed 
    def now(self):
        return datetime.now(timezone.utc)
    def elapsed_sec(self, started_at: datetime, until: datetime | None = None)->int:
        if until is None:
            return int((self.now() - started_at).total_seconds()*self.speed)
        return int((until - started_at).total_seconds() *self.speed)
    
