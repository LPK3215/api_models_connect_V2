from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.state import get_config_service

router = APIRouter(tags=["prompts"])


class PromptUpsert(BaseModel):
    name: str = Field(min_length=1)
    category: str = Field(default="通用")
    description: str = Field(default="")
    prompt: str = Field(min_length=1)
    tags: List[str] = Field(default_factory=list)


@router.get("/prompts")
def list_prompts() -> dict:
    prompts = get_config_service().get_all_prompts()

    items = []
    for p in prompts:
        items.append(
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "category": p.get("category"),
                "description": p.get("description"),
                "tags": p.get("tags", []),
                "created_at": p.get("created_at"),
                "updated_at": p.get("updated_at"),
            }
        )

    return {"items": items}


@router.get("/prompts/{prompt_id}")
def get_prompt(prompt_id: str) -> dict:
    prompt = get_config_service().get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return {
        "id": prompt.get("id"),
        "name": prompt.get("name"),
        "category": prompt.get("category"),
        "description": prompt.get("description"),
        "tags": prompt.get("tags", []),
        "created_at": prompt.get("created_at"),
        "updated_at": prompt.get("updated_at"),
        "prompt": prompt.get("prompt"),
    }


@router.post("/prompts")
def upsert_prompt(payload: PromptUpsert) -> dict:
    ok, msg = get_config_service().save_prompt(
        name=payload.name,
        category=payload.category,
        description=payload.description,
        content=payload.prompt,
        tags=payload.tags,
    )

    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return {"ok": True, "message": msg}


@router.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: str) -> dict:
    ok, msg = get_config_service().delete_prompt(prompt_id)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"ok": True, "message": msg}
