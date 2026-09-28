from __future__ import annotations
from dataclasses import dataclass

@dataclass # use to simply claass that use specially for data collection
class Settings:
    min_success_minutes:int = 15
    demo_speed:float = 1.0
    save_path:str =  "save.json"
    species_seed_path:str = "seed/species.json"
    min_room_members:int = 2
    max_room_members:int = 6