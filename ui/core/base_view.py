from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

import flet as ft

from app.errors import AppError

if TYPE_CHECKING:
    from ui.core.app_context import AppContext


class BaseView(ABC):
    #class variables
    route: ClassVar[str] = "/"
    requires_player: ClassVar[bool] = True

    def __init__(self, ctx : AppContext, **params: Any) -> None: 
        self.ctx = ctx
        self.params: dict[str,Any] = dict(params)

    @abstractmethod
    def build(self) -> ft.Control:
        raise NotImplementedError

    def on_enter(self) -> None:
        return None

    def on_leave(self) -> None:
        return None

    def show_error(self, error: AppError) -> None:
        snack_bar = ft.SnackBar(
            content=ft.Text(error.message, color=ft.colors.WHITE),
            bgcolor=ft.colors.RED_600,
        )
        self.ctx.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.ctx.page.update()

    def to_view(self) -> ft.View:
        return ft.View(self.route,[self.build()])
