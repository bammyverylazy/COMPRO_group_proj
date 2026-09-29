from __future__ import annotations

import json
from pathlib import Path

from app.config import Settings
from app.core.clock import Clock
from app.data.game_store import GameStore
from app.domain.enums import EggTier
from app.errors import AppError
from app.services.player_service import PlayerService

PLAY_DIR = Path("playground")
SAMPLE_SPECIES = [
    {"code": "debug_duck", "name": "Debug Duck", "tier": "freshman", "rarity": "common", "sprite_path": "sprites/debug_duck.png"},
    {"code": "loop_lizard", "name": "Loop Lizard", "tier": "freshman", "rarity": "rare", "sprite_path": "sprites/loop_lizard.png"},
    {"code": "stack_sloth", "name": "Stack Sloth", "tier": "senior", "rarity": "common", "sprite_path": "sprites/stack_sloth.png"},
    {"code": "kernel_kitsune", "name": "Kernel Kitsune", "tier": "senior", "rarity": "legendary", "sprite_path": "sprites/kernel_kitsune.png"},
    {"code": "turing_tortoise", "name": "Turing Tortoise", "tier": "professor", "rarity": "legendary", "sprite_path": "sprites/turing_tortoise.png"},
]


def make_settings() -> Settings:
    PLAY_DIR.mkdir(exist_ok=True)
    seed_path = PLAY_DIR / "species.json"
    if not seed_path.exists():
        seed_path.write_text(json.dumps(SAMPLE_SPECIES, ensure_ascii=False, indent=2), encoding="utf-8")
    settings = Settings()
    settings.save_path = str(PLAY_DIR / "save.json")
    settings.species_seed_path = str(seed_path)
    return settings


def show_menu() -> None:
    print()
    print("1) ดูผู้เล่นทั้งหมด")
    print("2) สร้างผู้เล่น")
    print("3) หาผู้เล่นจาก id")
    print("4) ดูสัตว์แยกตามระดับไข่")
    print("5) ดูไฟล์ save.json")
    print("6) ปิดแล้วเปิด store ใหม่ (เช็กว่าข้อมูลไม่หาย)")
    print("0) ออก")


def main() -> None:
    settings = make_settings()
    clock = Clock(settings.demo_speed)
    store = GameStore.open(settings)
    players = PlayerService(store, clock)
    print(f"เปิด store แล้ว · สัตว์ {len(store.species.list_all())} ชนิด · ผู้เล่น {len(store.players.list_all())} คน")
    while True:
        show_menu()
        choice = input("เลือก: ").strip()
        try:
            if choice == "1":
                for player in players.list_players():
                    print(f"  #{player.id} {player.nickname}")
            elif choice == "2":
                print("  สร้างแล้ว:", players.create_player(input("  ชื่อเล่น: ")))
            elif choice == "3":
                print("  เจอ:", players.get_player(int(input("  id: "))))
            elif choice == "4":
                for tier in EggTier:
                    names = [species.name for species in store.species.list_by_tier(tier)]
                    print(f"  {tier.value}: {', '.join(names)}")
            elif choice == "5":
                path = Path(settings.save_path)
                print(path.read_text(encoding="utf-8") if path.exists() else "  ยังไม่มีไฟล์ save.json (ลองสร้างผู้เล่นก่อน)")
            elif choice == "6":
                store = GameStore.open(settings)
                players = PlayerService(store, clock)
                print(f"  เปิดใหม่แล้ว · ผู้เล่น {len(store.players.list_all())} คน")
            elif choice == "0":
                break
            else:
                print("  ไม่มีเมนูนี้")
        except AppError as error:
            print(f"  [{type(error).__name__}] {error.message}" + (f" (ช่อง {error.field})" if error.field else ""))
        except ValueError:
            print("  id ต้องเป็นตัวเลข")


if __name__ == "__main__":
    main()
