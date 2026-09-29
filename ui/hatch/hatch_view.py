from __future__ import annotations

from typing import ClassVar

import flet as ft

from ui.core.base_view import BaseView


class HatchView(BaseView):
    route: ClassVar[str] = "/hatch"

    def build(self) -> ft.Control:
        return ft.Text("Hatch (F4 ยังไม่ได้ทำ)")
