from __future__ import annotations
from typing import Any
import flet as ft
import flet_audio as fta

class SoundManager:
    def __init__(self, page: ft.Page, muted: bool = False) -> None:
        self.page = page
        self.muted = muted
        self._sounds: dict[str, Any] = {}

    def load(self,name:str,path:str) -> None:
        audio = fta.Audio(src=path)
        self.page.overlay.append(audio)
        self._sounds[name] = audio
        self.page.update()

    def play(self,name:str) -> None:
        if self.muted:
            return 
        audio = self._sounds.get(name)
        if audio is not None:
            audio.play()

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        return self.muted
