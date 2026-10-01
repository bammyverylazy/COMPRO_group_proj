from __future__ import annotations

import flet as ft

from app.config import Settings
from ui.core.app_context import AppContext


def main(page: ft.Page) -> None:
    page.title = "CPEgg Hatch"
    page.window.width = 450
    page.window.height = 800
    page.window.resizable = False
    page.padding = 0
    page.spacing = 0
    ctx = AppContext.create(page, Settings())
    ctx.nav.start()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")