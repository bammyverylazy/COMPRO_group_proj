from __future__ import annotations

from typing import Any

import flet as ft

try:
    import flet_audio as fta
except ImportError:
    fta = None


class SoundManager:
    def __init__(self, page: ft.Page, muted: bool = False) -> None:
        self.page = page
        self.muted = muted
        self._sounds: dict[str, Any] = {}
        self._current: str | None = None

    def load(self, name: str, path: str) -> None:
        if fta is None:
            return

        audio = fta.Audio(
            src=path,
            autoplay=(name == "landing_lobby"),
            volume=1.0,
            release_mode=fta.ReleaseMode.LOOP,
        )

        self.page.services.append(audio)
        self._sounds[name] = audio

        if name == "landing_lobby":
            self._current = name

        self.page.update()

    def play(self, name: str) -> None:
        if self.muted:
            return

        if self._current == name:
            return

        if self._current is not None:
            current_audio = self._sounds.get(self._current)
            if current_audio is not None:
                self.page.run_task(current_audio.pause)

        audio = self._sounds.get(name)

        if audio is not None:
            self.page.run_task(audio.play)
            self._current = name

    def stop(self) -> None:
        if self._current is None:
            return

        audio = self._sounds.get(self._current)
        if audio is not None:
            self.page.run_task(audio.pause)

        self._current = None

    def toggle_mute(self) -> bool:
        self.muted = not self.muted

        if self.muted:
            self.stop()

        return self.muted