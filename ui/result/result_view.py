from __future__ import annotations

from typing import ClassVar

import flet as ft

from ui.core.base_view import BaseView


class ResultView(BaseView):
    route: ClassVar[str] = "/result"

    def build(self) -> ft.Control:
        return ft.Text("Result (F3 ยังไม่ได้ทำ)")
