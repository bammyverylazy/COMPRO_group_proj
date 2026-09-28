from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.errors import InvalidStateError

if TYPE_CHECKING:
    from ui.core.app_context import AppContext
    from ui.core.base_view import BaseView


class Navigator():
    def __init__(self,ctx: AppContext) -> None:
        self.ctx = ctx
        self.routes: dict[str, type[BaseView]] = {}
        self.current: BaseView | None = None

    def register(self,view_cls: type[BaseView]) -> None:
        self.routes[view_cls.route] = view_cls

    def start(self) -> None:
        self._register_all_routes()
        self.go("/")

    def go(self, route: str, **params: Any) -> None:
        view_cls = self.routes.get(route)
        if view_cls is None:
            raise InvalidStateError(f"Route '{route}' is not registered.")
        if self.current is not None:
            self.current.on_leave()
        if view_cls.requires_player and self.ctx.player is None:
            view_cls = self.routes["/"]
            params = {}
        view = view_cls(self.ctx, **params)
        self.current = view
        self.ctx.page.views.clear()
        self.ctx.page.views.append(view.to_view())
        self.ctx.page.update()
        view.on_enter()

    def _register_all_routes(self) -> None:
        from ui.dex.dex_view import DexView
        from ui.focus.focus_view import FocusView
        from ui.hatch.hatch_view import HatchView
        from ui.landing.landing_view import LandingView
        from ui.lobby.lobby_view import LobbyView
        from ui.result.history_view import HistoryView
        from ui.result.result_view import ResultView
        from ui.room.room_focus_view import RoomFocusView
        from ui.room.room_setup_view import RoomSetupView

        view_classes: tuple[type[BaseView], ...] = (
            LandingView,
            LobbyView,
            FocusView,
            RoomSetupView,
            RoomFocusView,
            HatchView,
            ResultView,
            DexView,
            HistoryView,
        )
        for view_cls in view_classes:
            self.register(view_cls)