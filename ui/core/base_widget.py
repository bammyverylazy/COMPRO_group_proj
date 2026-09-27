from __future__ import annotations
from abc import ABC, abstractmethod
import flet as ft


class BaseWidget(ABC):
    def __init__(self) -> None:
        self._control: ft.Control | None = None

    @abstractmethod
    def build(self) -> ft.Control:
        raise NotImplementedError

    @property
    def control(self) -> ft.Control:
        if self._control is None:
            self._control = self.build()
        return self._control

    def refresh(self) -> None:
        self.control.update()

