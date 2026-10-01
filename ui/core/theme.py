from __future__ import annotations
import flet as ft
from app.domain.enums import Rarity

class Theme:
    PRIMARY: str = "#2F5BD8"
    ACCENT: str = "#F2913A"
    BACKGROUND: str = "#FFFFFF"
    TEXT: str = "#1D2333"
    MUTED: str = "#8A93A6"
    ERROR: str = "#D2412F"
    FONT_FAMILY: str = "Mali"
    MOBILE_BREAKPOINT: int = 600
    PAGE_PADDING: int = 16
    PANEL_PADDING: int = 16
    PANEL_RADIUS: int = 16
    PANEL_COLOR: str = "black54"
    SPACING: int = 12
    TITLE_SIZE: int = 26
    HEADING_SIZE: int = 18
    BODY_SIZE: int = 14
    SMALL_SIZE: int = 12
    CLOCK_SIZE: int = 64
    BUTTON_HEIGHT: int = 44
    IMAGE_BUTTON_HEIGHT: int = 52
    CONTENT_WIDTH: int = 400

    _RARITY_COLORS: dict[Rarity, str] = {
        Rarity.COMMON: "#8A93A6",
        Rarity.RARE: "#2F5BD8",
        Rarity.EPIC: "#8E4FE0",
        Rarity.LEGENDARY: "#F2913A",
    }

    @classmethod
    def apply(cls, page: ft.Page) -> None:
        page.title = "CPE Egg Hatch"
        page.fonts = {cls.FONT_FAMILY: cls.FONT_FAMILY}
        page.theme = ft.Theme(font_family=cls.FONT_FAMILY, color_scheme_seed=cls.PRIMARY)
        page.bgcolor = cls.BACKGROUND
        page.window.width = 420
        page.window.height = 800

    @classmethod
    def is_mobile(cls, page: ft.Page) -> bool:
        return page.width < cls.MOBILE_BREAKPOINT

    @classmethod
    def rarity_color(cls, rarity: Rarity) -> str:
        return cls._RARITY_COLORS[rarity]

