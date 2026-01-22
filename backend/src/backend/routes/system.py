from __future__ import annotations

from fastapi import APIRouter

from backend.state import get_config_service

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/system/status")
def system_status() -> dict:
    return get_config_service().get_system_status()
