from __future__ import annotations

from typing import Callable

import flet as ft
from app.dto import PlayerDTO
from ui.core.base_widget import BaseWidget
from ui.core.sound_manager import SoundManager
from ui.core.theme import Theme

MAX_NICKNAME_LENGTH = 20
FONT_PIXEL = getattr(Theme, "FONT_PIXEL", "Pixel")

BG_NORMAL = "#E8C88A"
BG_HOVER = "#FFE8AD"
BORDER_COLOR = "#6D4348"
TEXT_COLOR = "#734547"


class PlayerPicker(BaseWidget):

    def __init__(
        self,
        players: list[PlayerDTO],
        on_pick: Callable[[PlayerDTO], None],
        on_create: Callable[[str], None],
        sound: SoundManager,
    ) -> None:
        super().__init__()
        self.players = players
        self.on_pick = on_pick
        self.on_create = on_create
        self.sound = sound
        self.nickname_field: ft.TextField | None = None
        self.error_text: ft.Text | None = None

    def _create_hoverable_button(
        self,
        text: str,
        on_click_callback: Callable[[], None],
        width: int = 260,
    ) -> ft.Container:
        button_text = ft.Text(
            text,
            color=TEXT_COLOR,
            font_family=FONT_PIXEL,
            size=16,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        container = ft.Container(
            content=button_text,
            width=width,
            padding=10,
            bgcolor=BG_NORMAL,
            border=ft.Border.all(3, BORDER_COLOR),
            border_radius=8,
            ink=True,
            alignment=ft.Alignment(0, 0),
            animate=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
        )

        def handle_hover(e: ft.ControlEvent) -> None:
            is_hovered = e.data == "true" or e.data is True
            container.bgcolor = BG_HOVER if is_hovered else BG_NORMAL
            container.update()

        def handle_click(e: ft.ControlEvent) -> None:
            on_click_callback()

        container.on_hover = handle_hover
        container.on_click = handle_click
        self.sound.bind_button(container)
        return container

    def build(self) -> ft.Control:
        self.nickname_field = ft.TextField(
            hint_text="Enter Nickname...",
            hint_style=ft.TextStyle(color="white54", font_family=FONT_PIXEL),
            text_style=ft.TextStyle(color="white", font_family=FONT_PIXEL),
            counter=ft.Text(""),
            max_length=MAX_NICKNAME_LENGTH,
            border_color="white",
            focused_border_color=BG_HOVER,
            bgcolor="black26",
            border_radius=8,
            width=260,
            content_padding=10,
        )
        self.error_text = ft.Text(
            "",
            color="#FF6B6B",
            font_family=FONT_PIXEL,
            size=12,
            visible=False,
        )

        player_rows: list[ft.Control] = []
        for player in self.players:
            p_text = ft.Text(
                player.nickname,
                color="white",
                font_family=FONT_PIXEL,
                size=16,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            )
            p_container = ft.Container(
                content=p_text,
                width=260,
                padding=10,
                bgcolor="black48",
                border=ft.Border.all(1.5, "white"),
                border_radius=8,
                ink=True,
                alignment=ft.Alignment(0, 0),
                animate=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
                on_click=lambda _, selected=player: self.on_pick(selected),
            )

            def make_hover(c: ft.Container):
                def _on_hover(e: ft.ControlEvent):
                    is_hovered = e.data == "true" or e.data is True
                    c.bgcolor = "black87" if is_hovered else "black48"
                    c.border = (
                        ft.Border.all(1.5, BG_HOVER)
                        if is_hovered
                        else ft.Border.all(1.5, "white")
                    )
                    c.update()

                return _on_hover

            p_container.on_hover = make_hover(p_container)
            self.sound.bind_button(p_container)
            player_rows.append(p_container)

        create_button = self._create_hoverable_button(
            text="CREATE",
            on_click_callback=lambda: self.on_create(
                self.nickname_field.value if self.nickname_field else ""
            ),
        )

        return ft.Column(
            [
                ft.Text(
                    "Select Player",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="white",
                    font_family=FONT_PIXEL,
                ),
                ft.Column(
                    player_rows,
                    scroll=ft.ScrollMode.AUTO,
                    height=180,
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(color="white24", height=10),
                self.nickname_field,
                self.error_text,
                create_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

    def show_error(self, message: str) -> None:
        if self.error_text is not None:
            self.error_text.value = message
            self.error_text.visible = True
            if self.error_text.page is not None:
                self.error_text.update()