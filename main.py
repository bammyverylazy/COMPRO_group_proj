from __future__ import annotations

import flet as ft

from app.config import Settings
from ui.core.app_context import AppContext
from ui.core.theme import Theme


def main(page: ft.Page) -> None:
    Theme.apply(page)
    ctx = AppContext.create(page, Settings())
    ctx.nav.start()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")