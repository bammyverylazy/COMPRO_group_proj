from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.domain.enums import EggTier, Rarity
from app.domain.species import Species
from app.errors import AppError


class SpeciesLoader:
    REQUIRED_FIELDS = ("code", "name", "tier", "rarity", "sprite_path")

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[Species]:
        rows = self._read_rows()
        species_list = [self._to_species(row, index)
                        for index, row in enumerate(rows, start=1)]
        self._check_unique_codes(species_list)
        return species_list

    def _read_rows(self) -> list[dict[str, Any]]:
        if not self.path.is_file():
            raise AppError(f"ไม่พบไฟล์รายชื่อสัตว์ {self.path}")
        try:
            with self.path.open("r", encoding="utf-8") as file:
                rows = json.load(file)
        except json.JSONDecodeError as error:
            raise AppError(
                f"ไฟล์ {self.path.name} ไม่ใช่ JSON ที่ถูกต้อง") from error
        if not isinstance(rows, list):
            raise AppError(f"ไฟล์ {self.path.name} ต้องเป็น list ของสัตว์")
        return rows

    def _to_species(self, row: Any, index: int) -> Species:
        if not isinstance(row, dict):
            raise AppError(
                f"สัตว์ตัวที่ {index} ใน {self.path.name} ต้องเป็น object")
        missing = [field for field in self.REQUIRED_FIELDS if field not in row]
        if missing:
            raise AppError(f"สัตว์ตัวที่ {index} ขาด {', '.join(missing)}")
        try:
            tier = EggTier(row["tier"])
            rarity = Rarity(row["rarity"])
        except ValueError as error:
            raise AppError(
                f"สัตว์ {row['code']} มี tier หรือ rarity ไม่ถูกต้อง") from error
        return Species(
            code=row["code"],
            name=row["name"],
            tier=tier,
            rarity=rarity,
            sprite_path=row["sprite_path"],
            description=row.get("description", ""),
        )

    def _check_unique_codes(self, species_list: list[Species]) -> None:
        seen: set[str] = set()
        for species in species_list:
            if species.code in seen:
                raise AppError(f"code {species.code} ซ้ำใน {self.path.name}")
            seen.add(species.code)
