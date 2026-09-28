from __future__ import annotations

import flet as ft
from app.dto import PlayerDTO
from ui.core.base_widget import BaseWidget
from ui.core.theme import Theme

MAX_NICKNAME_LENGTH = 20


class PlayerPicker(BaseWidget):

    def __init__(
        self,
        players: list[PlayerDTO],
        on_pick: Callable[[PlayerDTO], None],
        on_create: Callable[[str], None],
    ) -> None:
        super().__init__()
        self.players = players
        self.on_pick = on_pick
        self.on_create = on_create
        self.nickname_field: ft.TextField | None = None
        self.error_text: ft.Text | None = None

    def build(self) -> ft.Control:
        self.nickname_field = ft.TextField(
            label="ชื่อเล่นใหม่", max_length=MAX_NICKNAME_LENGTH
        )
        self.error_text = ft.Text("", color=Theme.ERROR, visible=False)
        player_rows: list[ft.Control] = [
            ft.ListTile(
                title=ft.Text(player.nickname),
                on_click=lambda _, selected=player: self.on_pick(selected),
            )
            for player in self.players
        ]
        return ft.Column([
            ft.Text(
                "เลือกผู้เล่น",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=Theme.TEXT,
            ),
            ft.Column(player_rows, scroll=ft.ScrollMode.AUTO, height=200),
            ft.Divider(),
            self.nickname_field,
            self.error_text,
            # ✅ เปลี่ยนจาก ft.Button หรือ ft.ElevatedButton เป็น ft.FilledButton
            ft.FilledButton(
                content=ft.Text("CREATE", color=ft.Colors.WHITE),
                style=ft.ButtonStyle(
                bgcolor=Theme.PRIMARY,
                ),
                on_click=lambda _: self.on_create(self.nickname_field.value or ""),
            )
        ])

    def show_error(self, message: str) -> None:
        if self.error_text is not None:
            self.error_text.value = message
            self.error_text.visible = True
            self.refresh()


# --- ส่วนสคริปต์จำลองการใช้งาน (Mock Runner) ---
def main(page: ft.Page) -> None:
    page.title = "PlayerPicker Simulation"
    page.window.width = 400
    page.window.height = 600

    # 1. จำลองข้อมูล PlayerDTO
    mock_players = [
        PlayerDTO(id=1, nickname="Saimai_Za"),
        PlayerDTO(id=2, nickname="Pro_Gamer_007"),
        PlayerDTO(id=3, nickname="CPE_Student"),
    ]

    # 2. Callback เมื่อเลือกผู้เล่นที่มีอยู่
    def handle_pick(player: PlayerDTO) -> None:
        print(f"[PICK] เลือกผู้เล่น: {player.nickname} (ID: {player.id})")
        snack = ft.SnackBar(ft.Text(f"เข้าสู่ระบบด้วย: {player.nickname}"))
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # 3. Callback เมื่อกดปุ่มสร้างผู้เล่นใหม่
    def handle_create(nickname: str) -> None:
        clean_name = nickname.strip()
        print(f"[CREATE] กำลังสร้างผู้เล่นชื่อ: '{clean_name}'")

        # ตรวจสอบ Validation
        if not clean_name:
            picker.show_error("กรุณากรอกชื่อเล่นก่อนสร้างตัวละคร!")
            return

        if any(p.nickname == clean_name for p in picker.players):
            picker.show_error("ชื่อเล่นนี้มีผู้ใช้งานแล้ว!")
            return

        # จำลองการสร้างสำเร็จ
        new_player = PlayerDTO(id=len(picker.players) + 1, nickname=clean_name)
        picker.players.append(new_player)

        snack = ft.SnackBar(ft.Text(f"สร้างผู้เล่นใหม่เรียบร้อย: {clean_name}"))
        page.overlay.append(snack)
        snack.open = True

        # รีเฟรชหน้าจอ PlayerPicker
        picker.refresh()

    # 4. สร้าง instance ของ PlayerPicker และแสดงบนหน้าจอ
    picker = PlayerPicker(
        players=mock_players, on_pick=handle_pick, on_create=handle_create
    )

    page.add(picker.build())


if __name__ == "__main__":
    ft.run(main)