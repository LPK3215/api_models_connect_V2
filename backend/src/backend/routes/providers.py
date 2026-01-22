from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.state import get_config_service

router = APIRouter(tags=["providers"])


@router.get("/providers")
def list_providers() -> dict:
    providers = get_config_service().get_all_providers()

    items = []
    for key, provider in providers.items():
        info = provider.get("info", {}) if isinstance(provider, dict) else {}
        items.append(
            {
                "key": key,
                "display_name": info.get("display_name") or provider.get("display_name") or key,
                "defaults": info.get("defaults", {}),
            }
        )

    return {"items": sorted(items, key=lambda x: x["display_name"])}


@router.get("/providers/{provider_key}")
def get_provider(provider_key: str) -> dict:
    try:
        provider = get_config_service().get_provider_info(provider_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    info = provider.get("info", {}) if isinstance(provider, dict) else {}
    return {
        "key": provider_key,
        "display_name": info.get("display_name") or provider.get("display_name") or provider_key,
        "defaults": info.get("defaults", {}),
    }


@router.get("/providers/{provider_key}/models")
def list_models(provider_key: str) -> dict:
    try:
        models = get_config_service().get_models_by_provider(provider_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    items = []
    for key, model in (models or {}).items():
        items.append(
            {
                "key": key,
                "name": model.get("name"),
                "info": model.get("info"),
                "env_key": model.get("env_key"),
                "api_base_url": model.get("api_base_url"),
            }
        )

    return {"items": sorted(items, key=lambda x: x["key"]) }
