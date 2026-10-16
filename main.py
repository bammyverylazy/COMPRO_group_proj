from __future__ import annotations

import flet as ft

from app.config import Settings
from app.core.paths import resource
from ui.core.app_context import AppContext
from ui.core.device_save import DeviceSave
from ui.core.theme import Theme


async def main(page: ft.Page) -> None:
    Theme.apply(page)
    settings = Settings()
    device_save = await DeviceSave.open(page, settings)
    ctx = AppContext.create(page, settings, device_save.save_file)
    ctx.nav.start()


if __name__ == "__main__":
    ft.run(main, assets_dir=str(resource("assets")))
