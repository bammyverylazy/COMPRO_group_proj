from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import flet as ft

from app.config import Settings
from app.data.save_file import MemorySaveFile, SaveFile


class DeviceSave:
    KEY: str = "cpe_egg_hatch.save"

    def __init__(self, page: ft.Page, prefs: ft.SharedPreferences, data: dict[str, Any]) -> None:
        self.page = page
        self.prefs = prefs
        self.save_file = MemorySaveFile(data, on_write=self._queue)
        self._pending: str | None = None
        self._writing = False

    @classmethod
    async def open(cls, page: ft.Page, settings: Settings) -> DeviceSave:
        prefs = ft.SharedPreferences()
        data = await cls._read(prefs)
        if not data:
            data = cls._legacy_file(settings)
        return cls(page, prefs, data)

    @classmethod
    async def _read(cls, prefs: ft.SharedPreferences) -> dict[str, Any]:
        try:
            raw = await prefs.get(cls.KEY)
        except Exception:
            return {}
        if not isinstance(raw, str) or not raw:
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _legacy_file(settings: Settings) -> dict[str, Any]:
        try:
            return SaveFile(Path(settings.save_path)).read()
        except Exception:
            return {}

    def _queue(self, data: dict[str, Any]) -> None:
        self._pending = json.dumps(data, ensure_ascii=False)
        if not self._writing:
            self._writing = True
            self.page.run_task(self._flush)

    async def _flush(self) -> None:
        try:
            while self._pending is not None:
                raw = self._pending
                self._pending = None
                try:
                    await self.prefs.set(self.KEY, raw)
                except Exception:
                    return
        finally:
            self._writing = False
