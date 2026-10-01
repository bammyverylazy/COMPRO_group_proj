from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import flet as ft

from app.dto import HatchResult
from app.errors import AppError, InvalidStateError
from ui.core.base_view import BaseView
from ui.core.format import Format
from ui.core.theme import Theme
from ui.core.widgets import PixelButton
from ui.hatch.hatch_animation import HatchAnimation

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class HatchView(BaseView):
    route: ClassVar[str] = "/hatch"
    BACKGROUND_PATH: ClassVar[str] = "backgrounds/hatch_background.png"
    PANEL_COLOR: ClassVar[str] = "black54"
    TITLE: ClassVar[str] = "HATCHING..."
    TADA_SOUND: ClassVar[str] = "tada"
    WAITING_TEXT: ClassVar[str] = "กำลังฟัก..."

    def __init__(self, ctx: AppContext, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.results: list[HatchResult] = []
        self.current_index: int = 0
        self.animation: HatchAnimation | None = None
        self.name_text: ft.Text | None = None
        self.detail_text: ft.Text | None = None
        self.counter_text: ft.Text | None = None
        self.slot: ft.Container | None = None
        self.skip_button: PixelButton | None = None
        self.next_button: PixelButton | None = None

    def build(self) -> ft.Control:
        self.name_text = ft.Text(
            "",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )
        self.detail_text = ft.Text("", size=14, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER)
        self.counter_text = ft.Text("", size=12, color="white70")
        self.slot = ft.Container(
            width=HatchAnimation.AREA_SIZE,
            height=HatchAnimation.AREA_SIZE,
            alignment=ft.Alignment.CENTER,
        )
        self.skip_button = PixelButton("SKIP", self._skip, variant="secondary")
        self.next_button = PixelButton("NEXT", self.next)
        self.next_button.control.visible = False

        panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(self.TITLE, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    self.counter_text,
                    self.slot,
                    self.name_text,
                    self.detail_text,
                    ft.Row(
                        controls=[self.skip_button.control, self.next_button.control],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                tight=True,
            ),
            bgcolor=self.PANEL_COLOR,
            border_radius=16,
            padding=20,
        )

        return ft.Stack(
            controls=[
                ft.Image(
                    src=self.BACKGROUND_PATH,
                    fit=ft.BoxFit.COVER,
                    width=float("inf"),
                    height=float("inf"),
                ),
                ft.Container(
                    content=panel,
                    alignment=ft.Alignment.CENTER,
                    padding=16,
                    left=0,
                    right=0,
                    top=0,
                    bottom=0,
                ),
            ],
            expand=True,
        )

    def on_enter(self) -> None:
        try:
            self.results = self._hatch()
        except InvalidStateError:
            self.go_result()
            return
        except AppError as error:
            self.show_error(error)
            return
        if not self.results:
            self.go_result()
            return
        self.current_index = 0
        self.play_current()

    def play_current(self) -> None:
        if self.slot is None or self.current_index >= len(self.results):
            return
        result = self.results[self.current_index]
        self.animation = HatchAnimation(result.tier, result.pet)
        self.slot.content = self.animation.control
        self._set_texts(result, revealed=False)
        self._set_buttons(playing=True)
        self.slot.update()
        self.ctx.sound.play(self.TADA_SOUND)
        self.animation.play(self.ctx.page, self._on_animation_done)

    def next(self) -> None:
        self.current_index += 1
        if self.current_index >= len(self.results):
            self.go_result()
            return
        self.play_current()

    def go_result(self) -> None:
        session_id = self.params.get("session_id")
        room_id = self.params.get("room_id")
        if room_id is not None:
            self.ctx.nav.go("/result", room_id=room_id)
            return
        self.ctx.nav.go("/result", session_id=session_id)

    def _hatch(self) -> list[HatchResult]:
        session_id = self.params.get("session_id")
        room_id = self.params.get("room_id")
        if room_id is not None:
            return list(self.ctx.rooms.hatch(int(room_id)).results)
        if session_id is not None:
            return [self.ctx.hatch.hatch(int(session_id))]
        return []

    def _skip(self) -> None:
        if self.animation is not None:
            self.animation.skip()

    def _on_animation_done(self) -> None:
        if self.current_index >= len(self.results):
            return
        self._set_texts(self.results[self.current_index], revealed=True)
        self._set_buttons(playing=False)

    def _set_texts(self, result: HatchResult, revealed: bool) -> None:
        if self.name_text is None or self.detail_text is None or self.counter_text is None:
            return
        nickname = self.ctx.players.get_player(result.player_id).nickname
        if len(self.results) > 1:
            self.counter_text.value = f"{self.current_index + 1} / {len(self.results)} · {nickname}"
        else:
            self.counter_text.value = ""
        if revealed:
            badge = "ตัวใหม่!" if result.is_new else f"Level up! Lv.{result.pet.level}"
            self.name_text.value = f"Congrats! {nickname} got {result.pet.species.name}"
            self.detail_text.value = f"{Format.tier_name(result.tier)} · {result.pet.species.rarity.value.upper()} · {badge}"
            self.detail_text.color = Theme.rarity_color(result.pet.species.rarity)
        else:
            self.name_text.value = self.WAITING_TEXT
            self.detail_text.value = ""
        self._safe_update(self.name_text, self.detail_text, self.counter_text)

    def _set_buttons(self, playing: bool) -> None:
        if self.skip_button is None or self.next_button is None:
            return
        last = self.current_index >= len(self.results) - 1
        self.skip_button.control.visible = playing
        self.next_button.control.visible = not playing
        self.next_button.control.content = ft.Text("SEE RESULT" if last else "NEXT", color=ft.Colors.WHITE)
        self._safe_update(self.skip_button.control, self.next_button.control)

    def _safe_update(self, *controls: ft.Control) -> None:
        for control in controls:
            try:
                control.update()
            except RuntimeError:
                continue
