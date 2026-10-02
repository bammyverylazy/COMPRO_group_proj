from __future__ import annotations

import os
from dataclasses import dataclass, field

from app.core.paths import data_file, resource


def _demo_speed() -> float:
    try:
        return max(1.0, float(os.environ.get("EGG_DEMO_SPEED", "1")))
    except ValueError:
        return 1.0


@dataclass
class Settings:
    min_success_minutes: int = 15
    demo_speed: float = field(default_factory=_demo_speed)
    save_path: str = field(default_factory=lambda: str(data_file("save.json")))
    species_seed_path: str = field(default_factory=lambda: str(resource("seed/species.json")))
    min_room_members: int = 2
    max_room_members: int = 6
