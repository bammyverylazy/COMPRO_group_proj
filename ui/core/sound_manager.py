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
        self._last_played: str | None = None
        self.volume_level: int = 10

    def load(self, name: str, path: str) -> None:
        if fta is None:
            return

        audio = fta.Audio(
            src=path,
            autoplay=(name == "landing_lobby"),
            volume=self._get_volume(),
            release_mode=fta.ReleaseMode.LOOP,
        )

        self.page.services.append(audio)
        self._sounds[name] = audio

        if name == "landing_lobby":
            self._current = name
            self._last_played = name

        self.page.update()

    def play(self, name: str) -> None:
        if self.muted or self.volume_level == 0:
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
            self._last_played = name

    def stop(self) -> None:
        if self._current is None:
            return

        audio = self._sounds.get(self._current)

        if audio is not None:
            self.page.run_task(audio.pause)

        self._current = None

    def increase_volume(self) -> int:
        was_zero = self.volume_level == 0

        if self.volume_level < 10:
            self.volume_level += 1
            self.muted = False
            self._apply_volume()

        if was_zero and self._last_played is not None:
            self.play(self._last_played)

        return self.volume_level

    def decrease_volume(self) -> int:
        if self.volume_level > 0:
            self.volume_level -= 1
            self._apply_volume()

        if self.volume_level == 0:
            self.muted = True
            self.stop()

        return self.volume_level

    def _get_volume(self) -> float:
        if self.muted:
            return 0.0

        return self.volume_level / 10

    def _apply_volume(self) -> None:
        volume = self._get_volume()

        for audio in self._sounds.values():
            audio.volume = volume

        self.page.update()

    def toggle_mute(self) -> bool:
        self.muted = not self.muted

        if self.muted:
            self._apply_volume()
            self.stop()
        else:
            if self.volume_level == 0:
                self.volume_level = 10

            self._apply_volume()

            if self._last_played is not None:
                self.play(self._last_played)

        return self.muted