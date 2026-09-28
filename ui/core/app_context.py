from __future__ import annotations

import flet as ft

from app.config import Settings
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.dto import PlayerDTO
from app.errors import InvalidStateError
from app.services.analytics_service import AnalyticsService
from app.services.dex_service import DexService
from app.services.focus_service import FocusSessionService
from app.services.hatch_service import HatchService
from app.services.player_service import PlayerService
from app.services.room_service import RoomService
from app.services.sanctuary_service import SanctuaryService
from app.services.tier_service import TierService
from ui.core.navigator import Navigator
from ui.core.sound_manager import SoundManager


class AppContext:
    def __init__(self,page: ft.Page,settings: Settings,store: GameStore) -> None:
        self.page = page
        self.settings = settings
        self.store = store
        self.clock = Clock(settings.demo_speed)
        self.player: PlayerDTO | None = None
        self.players = PlayerService(store, self.clock)
        self.tiers = TierService()
        self.focus = FocusSessionService(store, self.clock, settings)
        self.hatch = HatchService(store)
        self.rooms = RoomService(store, self.clock, settings, self.hatch)
        self.sanctuary = SanctuaryService(store)
        self.dex = DexService(store)
        self.analytics = AnalyticsService(store, settings)
        self.sound = SoundManager(page)
        self.nav = Navigator(self)

    @classmethod
    def create(cls, page: ft.Page, settings: Settings) -> AppContext:
        store = GameStore.open(settings)
        return cls(page, settings, store)

    def require_player(self) -> PlayerDTO:
        if self.player is None:
            raise InvalidStateError("Player is not set in AppContext.")
        return self.player