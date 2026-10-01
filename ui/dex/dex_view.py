from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import flet as ft

from app.domain.enums import EggTier
from app.dto import DexEntry
from app.errors import AppError
from ui.core.base_view import BaseView
from ui.core.format import Format
from ui.core.theme import Theme
from ui.core.widgets import PixelButton
from ui.dex.dex_card import DexCard
from ui.dex.dex_detail_panel import DexDetailPanel

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class DexView(BaseView):
    route: ClassVar[str] = "/dex"
    BACKGROUND_PATH: ClassVar[str] = "backgrounds/dex_background.png"
    TITLE: ClassVar[str] = "CPE DEX"
    PANEL_COLOR: ClassVar[str] = "black54"
    TIER_ORDER: ClassVar[tuple[EggTier, ...]] = (
        EggTier.FRESHMAN,
        EggTier.SENIOR,
        EggTier.PROFESSOR,
    )

    def __init__(self, ctx: AppContext, **params: Any) -> None:
        super().__init__(ctx, **params)
        self.entries: list[DexEntry] = []
        self.cards: list[DexCard] = []
        self.detail: DexDetailPanel | None = None
        self.completion_text: ft.Text | None = None
        self.progress: ft.ProgressBar | None = None
        self.sections: ft.Column | None = None

    def build(self) -> ft.Control:
        self.detail = DexDetailPanel()
        self.completion_text = ft.Text("", color=ft.Colors.WHITE, size=14)
        self.progress = ft.ProgressBar(value=0.0, color=Theme.ACCENT, bgcolor="white24", bar_height=8)
        self.sections = ft.Column(controls=[], spacing=12, tight=True)
        back_button = PixelButton("BACK", self.close, variant="secondary")

        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(self.TITLE, size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            back_button.control,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.completion_text,
                    self.progress,
                ],
                spacing=8,
                tight=True,
            ),
            bgcolor=self.PANEL_COLOR,
            border_radius=16,
            padding=16,
        )

        body = ft.Column(
            controls=[header, self.detail.control, self.sections],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            expand=True,
        )

        return ft.Stack(
            controls=[
                ft.Image(
                    src=self.BACKGROUND_PATH,
                    fit=ft.BoxFit.COVER,
                    width=float("inf"),
                    height=float("inf"),
                ),
                ft.Container(content=body, padding=16, left=0, right=0, top=0, bottom=0),
            ],
            expand=True,
        )

    def on_enter(self) -> None:
        player = self.ctx.require_player()
        try:
            self.entries = self.ctx.dex.list_entries(player.id)
            completion = self.ctx.dex.completion(player.id)
        except AppError as error:
            self.show_error(error)
            return
        unlocked = sum(1 for entry in self.entries if entry.unlocked)
        if self.completion_text is not None:
            self.completion_text.value = f"สะสมแล้ว {unlocked} / {len(self.entries)} ตัว ({Format.percent(completion)})"
            self.completion_text.update()
        if self.progress is not None:
            self.progress.value = completion
            self.progress.update()
        self._render_sections()
        first = next((entry for entry in self.entries if entry.unlocked), None)
        if first is None and self.entries:
            first = self.entries[0]
        if first is not None:
            self.select(first)

    def select(self, entry: DexEntry) -> None:
        for card in self.cards:
            card.set_selected(card.entry.species.code == entry.species.code)
        if self.detail is not None:
            self.detail.show(entry)

    def close(self) -> None:
        self.ctx.nav.go("/lobby")

    def _render_sections(self) -> None:
        if self.sections is None:
            return
        self.cards = []
        controls: list[ft.Control] = []
        for tier in self.TIER_ORDER:
            tier_entries = [entry for entry in self.entries if entry.species.tier is tier]
            if not tier_entries:
                continue
            tier_cards = [DexCard(entry, self.select) for entry in tier_entries]
            self.cards.extend(tier_cards)
            unlocked = sum(1 for entry in tier_entries if entry.unlocked)
            controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"{Format.tier_name(tier)} · {unlocked}/{len(tier_entries)}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Row(controls=[card.control for card in tier_cards], wrap=True, spacing=8, run_spacing=8),
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    bgcolor=self.PANEL_COLOR,
                    border_radius=16,
                    padding=12,
                )
            )
        self.sections.controls = controls
        self.sections.update()
