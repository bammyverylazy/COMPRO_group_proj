from __future__ import annotations

from typing import ClassVar

import flet as ft

from ui.core.base_view import BaseView


class FocusView(BaseView):
    route: ClassVar[str] = "/focus"

    def build(self) -> ft.Control:
        return ft.Text("Focus (F2 ยังไม่ได้ทำ)")
