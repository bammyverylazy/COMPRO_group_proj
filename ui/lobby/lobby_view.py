from __future__ import annotations

from typing import ClassVar

import flet as ft

from ui.core.base_view import BaseView


class LobbyView(BaseView):
    route: ClassVar[str] = "/lobby"

    def build(self) -> ft.Control:
        return ft.Text("Lobby (F4 ยังไม่ได้ทำ)")
