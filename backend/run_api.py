#!/usr/bin/env python3
"""Run the backend API (FastAPI).

This file lives at backend/ so the repo root can stay documentation-only.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap() -> None:
    backend_root = Path(__file__).resolve().parent
    src_dir = backend_root / "src"
    sys.path.insert(0, str(src_dir))


def main() -> None:
    _bootstrap()
    from backend.run import main as run_main

    run_main()


if __name__ == "__main__":
    main()

