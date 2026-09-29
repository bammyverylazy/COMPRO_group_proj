import flet as ft
from ui.core.base_view import BaseView


class DexView(BaseView):
    route = "/dex"

    def build(self) -> ft.Control:
        return ft.Text("Dex View (Mock)")