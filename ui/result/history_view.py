from __future__ import annotations

from typing import ClassVar

import flet as ft

from ui.core.base_view import BaseView


class HistoryView(BaseView):
    route: ClassVar[str] = "/history"

    def build(self) -> ft.Control:
        return ft.Text("History (F3 ยังไม่ได้ทำ)")
