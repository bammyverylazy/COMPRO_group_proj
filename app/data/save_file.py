from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.errors import AppError


class SaveFile:
    def __init__(self, path: Path) -> None:
        self.path = path

    def exists(self) -> bool:
        return self.path.is_file()

    def read(self) -> dict[str, Any]:
        if not self.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise AppError(f"ไฟล์ {self.path.name} เสีย อ่านไม่ได้") from error
        if not isinstance(data, dict):
            raise AppError(f"ไฟล์ {self.path.name} รูปแบบไม่ถูกต้อง")
        return data

    def write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_name(self.path.name + ".tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temp_path.replace(self.path)
