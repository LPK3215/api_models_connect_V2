from __future__ import annotations

from pathlib import Path


def safe_filename(name: str) -> str:
    name = name.replace("\\", "_").replace("/", "_").strip()
    return name or "upload"


def project_root() -> Path:
    # backend/src/backend/util.py -> project root is backend/
    return Path(__file__).resolve().parent.parent.parent
