from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.state import get_config_service, get_processor
from backend.util import safe_filename

router = APIRouter(tags=["tasks"])


@router.post("/tasks/process")
async def process_images(
    provider: str = Form(...),
    model: str = Form(...),
    prompt_id: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
    request_delay: float = Form(0.2),
    max_retries: int = Form(2),
    retry_delay: float = Form(1.0),
    timeout: float = Form(60.0),
    enable_compression: bool = Form(True),
    max_workers: int = Form(1),
    files: list[UploadFile] = File(...),
) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    resolved_prompt = prompt
    if prompt_id:
        p = get_config_service().get_prompt_by_id(prompt_id)
        if not p:
            raise HTTPException(status_code=404, detail="Prompt not found")
        resolved_prompt = p.get("prompt")

    if not resolved_prompt:
        raise HTTPException(status_code=400, detail="prompt or prompt_id is required")

    image_paths: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="api_models_connect_") as tmp:
        tmp_dir = Path(tmp)
        for f in files:
            name = safe_filename(f.filename or "upload")
            dst = tmp_dir / name
            dst.write_bytes(await f.read())
            image_paths.append(dst)

        try:
            result = get_processor().process(
                provider_key=provider,
                model_key=model,
                images=image_paths,
                prompt=resolved_prompt,
                request_delay=request_delay,
                max_retries=max_retries,
                retry_delay=retry_delay,
                timeout=timeout,
                enable_compression=enable_compression,
                max_workers=max_workers,
                verbose=False,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    try:
        summary = result.get("summary", {}) if isinstance(result, dict) else {}
        totals = summary.get("totals", {}) if isinstance(summary, dict) else {}
        get_config_service().add_task_record(
            provider=provider,
            model=model,
            file_count=int(totals.get("all") or len(files)),
            success_count=int(totals.get("success") or 0),
            failed_count=int(totals.get("failed") or 0),
            output_dir=summary.get("output_dir"),
        )
    except Exception:
        pass

    return result
