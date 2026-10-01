from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Callable

import flet as ft

from app.core.clock import Clock


class StopwatchTimer:
    def __init__(
        self,
        clock: Clock,
        started_at: datetime,
        on_tick: Callable[[int], None],
        interval_sec: float = 1.0,
    ) -> None:
        self.clock: Clock = clock
        self.started_at: datetime = started_at
        self.on_tick: Callable[[int], None] = on_tick
        self.interval_sec: float = interval_sec
        self.running: bool = False

    def start(self, page: ft.Page) -> None:
        if self.running:
            return
        self.running = True
        page.run_task(self._loop)

    def stop(self) -> None:
        self.running = False

    @property
    def elapsed_sec(self) -> int:
        return self.clock.elapsed_sec(self.started_at)

    async def _loop(self) -> None:
        while self.running:
            self.on_tick(self.elapsed_sec)
            await asyncio.sleep(self.interval_sec)
