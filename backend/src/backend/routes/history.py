from __future__ import annotations

from fastapi import APIRouter

from backend.state import get_config_service

router = APIRouter(tags=["history"])


@router.get("/history")
def get_history() -> dict:
    return {"items": get_config_service().get_task_history()}


@router.delete("/history")
def clear_history() -> dict:
    ok, msg = get_config_service().clear_task_history()
    return {"ok": ok, "message": msg}
