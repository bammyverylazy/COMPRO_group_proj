from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

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
            raise AppError(f"Save file {self.path.name} is corrupted") from error
        if not isinstance(data, dict):
            raise AppError(f"Save file {self.path.name} has an invalid format")
        return data

    def write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_name(self.path.name + ".tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temp_path.replace(self.path)


class MemorySaveFile:
    def __init__(
        self,
        data: dict[str, Any] | None = None,
        on_write: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.data: dict[str, Any] = dict(data or {})
        self.on_write = on_write

    def exists(self) -> bool:
        return bool(self.data)

    def read(self) -> dict[str, Any]:
        return dict(self.data)

    def write(self, data: dict[str, Any]) -> None:
        self.data = dict(data)
        if self.on_write is not None:
            self.on_write(self.data)
