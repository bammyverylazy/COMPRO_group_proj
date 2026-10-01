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

    def __init__(
        self,
        ctx: AppContext,
        **params: object,
    ) -> None:
        super().__init__(ctx, **params)
        self.scene: SanctuaryScene | None = None

    def _viewport_width(self) -> float:
        page_width = self.ctx.page.width or self.MAP_WIDTH
        return min(page_width, self.MAP_WIDTH)

    def _viewport_height(self) -> float:
        page_height = self.ctx.page.height or self.MAP_HEIGHT
        return min(page_height, self.MAP_HEIGHT)

    def _minimum_scale(self) -> float:
        page_width = self.ctx.page.width or self.MAP_WIDTH
        page_height = self.ctx.page.height or self.MAP_HEIGHT

        if page_width < self.MAP_WIDTH:
            return page_height / self.MAP_HEIGHT

        return 1.0

    def build(self) -> ft.Control:
        self.scene = SanctuaryScene(
            width=self.MAP_WIDTH,
            height=self.MAP_HEIGHT,
        )

        viewer = ft.InteractiveViewer(
            width=self._viewport_width(),
            height=self._viewport_height(),
            constrained=False,
            pan_enabled=True,
            scale_enabled=True,
            min_scale=self._minimum_scale(),
            max_scale=self.MAX_SCALE,
            boundary_margin=ft.Margin.all(0),
            content=self.scene.build(),
        )

        return ft.Container(
            expand=True,
            bgcolor=ft.Colors.BLACK,
            alignment=ft.Alignment.CENTER,
            content=viewer,
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