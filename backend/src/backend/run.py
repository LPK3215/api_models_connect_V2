#!/usr/bin/env python3
"""启动 FastAPI 后端（开发模式）。"""

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
            f"端口 {port} 已被占用。"
            f"请设置 API_PORT 为可用端口，并同步修改 frontend/.env.development -> VITE_API_ORIGIN。"
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
