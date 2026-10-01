from __future__ import annotations

from functools import partial
from typing import Callable, ClassVar, TYPE_CHECKING

import flet as ft

from app.dto import SessionDTO
from app.errors import AppError
from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme
from ui.core.widgets import PixelButton
from ui.hatch.egg_odds_panel import EggOddsPanel

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class SetupPopup(BaseWidget):
    WIDTH: ClassVar[int] = 360
    SPACING: ClassVar[int] = 12
    SECTION_SIZE: ClassVar[int] = 14
    RECENT_LABEL: ClassVar[str] = "Recent subjects"
    FIELD_LABEL: ClassVar[str] = "Subject"

    def __init__(
        self,
        ctx: AppContext,
        on_started: Callable[[SessionDTO], None],
        on_back: Callable[[], None],
    ) -> None:
        super().__init__()
        self.ctx: AppContext = ctx
        self.on_started: Callable[[SessionDTO], None] = on_started
        self.on_back: Callable[[], None] = on_back
        self.subject_field: ft.TextField | None = None
        self.error_text: ft.Text | None = None
        self.odds_panel: EggOddsPanel | None = None

    def build(self) -> ft.Control:
        self.subject_field = ft.TextField(
            label=self.FIELD_LABEL,
            autofocus=True,
            on_submit=self._on_submit,
        )
        self.error_text = ft.Text("", color=Theme.ERROR, visible=False)
        self.odds_panel = EggOddsPanel(self.ctx.tiers.list_odds())
        controls: list[ft.Control] = [self.subject_field]
        controls.extend(self._build_recent())
        controls.extend([self.odds_panel.control, self.error_text, self._build_actions()])
        return ft.Column(controls=controls, spacing=self.SPACING, tight=True, width=self.WIDTH)

    @property
    def subject(self) -> str:
        if self.subject_field is None:
            return ""
        return (self.subject_field.value or "").strip()

    def start(self) -> None:
        try:
            player_id: int = self.ctx.require_player().id
            session: SessionDTO = self.ctx.focus.start(player_id, self.subject)
        except AppError as error:
            self._show_error(error.message)
            return
        self.on_started(session)

    def _on_submit(self, event: ft.ControlEvent) -> None:
        self.start()

    def _build_recent(self) -> list[ft.Control]:
        subjects: list[str] = self._load_recent_subjects()
        if not subjects:
            return []
        label: ft.Text = ft.Text(self.RECENT_LABEL, size=self.SECTION_SIZE, color=Theme.MUTED)
        buttons: list[ft.Control] = [
            PixelButton(subject, partial(self._fill_subject, subject), variant="secondary").control
            for subject in subjects
        ]
        return [label, ft.Row(controls=buttons, wrap=True)]

    def _load_recent_subjects(self) -> list[str]:
        try:
            player_id: int = self.ctx.require_player().id
            return self.ctx.focus.recent_subjects(player_id)
        except AppError as error:
            self._show_error(error.message)
            return []

    def _build_actions(self) -> ft.Control:
        back_button: PixelButton = PixelButton("BACK", self.on_back, variant="secondary")
        start_button: PixelButton = PixelButton("START", self.start)
        return ft.Row(
            controls=[back_button.control, start_button.control],
            alignment=ft.MainAxisAlignment.END,
        )

    def _fill_subject(self, subject: str) -> None:
        if self.subject_field is None:
            return
        self.subject_field.value = subject
        self.subject_field.update()

    def _show_error(self, message: str) -> None:
        if self.error_text is None:
            return
        self.error_text.value = message
        self.error_text.visible = True
        if self._control is not None:
            self.error_text.update()
