from __future__ import annotations
import flet as ft

# --- Backend Services (B1, B2, B3) ---
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.services.analytics_service import AnalyticsService
from app.services.dex_service import DexService
from app.services.focus_session_service import FocusSessionService
from app.services.hatch_service import HatchService
from app.services.player_service import PlayerService
from app.services.room_service import RoomService
from app.services.sanctuary_service import SanctuaryService
from app.services.tier_service import TierService

# --- Frontend Views (F1, F2, F3, F4) ---
from ui.core.app_context import AppContext
from ui.core.navigator import Navigator
from ui.landing.landing_view import LandingView
# from ui.views.lobby_view import LobbyView
# from ui.views.focus_view import FocusView
# from ui.views.result_view import ResultView
# from ui.views.room_setup_view import RoomSetupView
# from ui.views.room_focus_view import RoomFocusView
# from ui.views.hatch_view import HatchView
# from ui.views.dex_view import DexView
# from ui.views.history_view import HistoryView


def main(page: ft.Page) -> None:
    # 1. Config Window
    page.title = "CPE Egg Hatch"
    page.window.width = 450
    page.window.height = 800
    page.window.resizable = False
    page.padding = 0
    page.spacing = 0

    # 2. Load Core Data & Clock
    store = GameStore.load("save.json")
    clock = Clock()

    # 3. Instantiate All Services
    player_service = PlayerService(store)
    tier_service = TierService()
    hatch_service = HatchService(store, tier_service, clock)
    focus_service = FocusSessionService(store, clock)
    room_service = RoomService(store, clock)
    sanctuary_service = SanctuaryService(store)
    dex_service = DexService(store)
    analytics_service = AnalyticsService(store)

    # 4. Inject Dependencies into AppContext
    ctx = AppContext(
        page=page,
        clock=clock,
        players=player_service,
        tiers=tier_service,
        hatch=hatch_service,
        focus=focus_service,
        rooms=room_service,
        sanctuary=sanctuary_service,
        dex=dex_service,
        analytics=analytics_service,
    )

    # 5. Route Registration
    navigator = Navigator(ctx)
    navigator.register_route("/", lambda: LandingView(ctx))
    
    # ลงทะเบียน Views ของเพื่อนๆ เมื่อเพื่อนทำเสร็จ
    # navigator.register_route("/lobby", lambda: LobbyView(ctx))
    # navigator.register_route("/focus", lambda: FocusView(ctx))
    # navigator.register_route("/result", lambda: ResultView(ctx))
    # navigator.register_route("/room/setup", lambda: RoomSetupView(ctx))
    # navigator.register_route("/room", lambda: RoomFocusView(ctx))
    # navigator.register_route("/hatch", lambda: HatchView(ctx))
    # navigator.register_route("/dex", lambda: DexView(ctx))
    # navigator.register_route("/history", lambda: HistoryView(ctx))

    # 6. Start App
    navigator.start()


if __name__ == "__main__":
    ft.app(target=main)