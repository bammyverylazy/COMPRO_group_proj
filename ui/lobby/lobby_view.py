from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import flet as ft

from ui.core.base_view import BaseView
from ui.lobby.sanctuary_scene import SanctuaryScene

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class LobbyView(BaseView):
    route: ClassVar[str] = "/lobby"

    MAP_WIDTH: ClassVar[float] = 1024
    MAP_HEIGHT: ClassVar[float] = 691
    MAX_SCALE: ClassVar[float] = 2.0

    def __init__(self, ctx: AppContext, **params: object) -> None:
        super().__init__(ctx, **params)
        self.scene: SanctuaryScene | None = None

    def build(self) -> ft.Control:
        self.scene = SanctuaryScene(
            width=self.MAP_WIDTH,
            height=self.MAP_HEIGHT,
        )

        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.InteractiveViewer(
                constrained=False,
                pan_enabled=True,
                scale_enabled=True,
                min_scale=1.0,
                max_scale=self.MAX_SCALE,
                boundary_margin=ft.Margin.all(0),
                content=self.scene.build(),
            ),
        )

    def on_enter(self) -> None:
        if self.scene is None:
            return

        player = self.ctx.require_player()
        pets = self.ctx.sanctuary.list_pets(player.id)

        self.scene.load(pets)
        self.scene.start(self.ctx.page)

    def on_leave(self) -> None:
        if self.scene is not None:
            self.scene.stop()