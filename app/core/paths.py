from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_DIR: Path = Path(__file__).resolve().parents[2]


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_dir() -> Path:
    bundled = getattr(sys, "_MEIPASS", None)
    return Path(bundled) if bundled else PROJECT_DIR


def app_dir() -> Path:
    return Path(sys.executable).resolve().parent if is_frozen() else PROJECT_DIR


def resource(relative: str) -> Path:
    for base in (bundle_dir(), app_dir(), PROJECT_DIR, Path.cwd()):
        candidate = base / relative
        if candidate.exists():
            return candidate
    return bundle_dir() / relative


def data_file(name: str) -> Path:
    storage = os.environ.get("FLET_APP_STORAGE_DATA")
    if storage:
        return Path(storage) / name
    return app_dir() / name
