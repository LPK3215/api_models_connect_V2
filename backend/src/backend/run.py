#!/usr/bin/env python3
"""Run FastAPI backend (development)."""

from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

import uvicorn

DEFAULT_PORT = 8000


def is_port_available(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            return sock.connect_ex(("127.0.0.1", port)) != 0
    except Exception:
        return False


def main() -> None:
    # Allow running from either repo root (`python -m backend`) or from inside the folder (`cd backend; python run.py`).
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    port = int(os.getenv("API_PORT") or DEFAULT_PORT)
    if not is_port_available(port):
        raise SystemExit(
            f"Port {port} is already in use. "
            f"Set API_PORT to a free port (and update frontend/.env.development -> VITE_API_ORIGIN)."
        )

    uvicorn.run(
        "backend.app:app",
        host="127.0.0.1",
        port=port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
