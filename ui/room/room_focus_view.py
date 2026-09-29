from __future__ import annotations

from typing import ClassVar

import flet as ft

from ui.core.base_view import BaseView


class RoomFocusView(BaseView):
    route: ClassVar[str] = "/room"

    def build(self) -> ft.Control:
        return ft.Text("Room Focus (F3 ยังไม่ได้ทำ)")
