from __future__ import annotations

import json
import queue
import shutil
import tempfile
import threading
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

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


@router.post("/tasks/process/stream")
async def process_images_stream(
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
):
    if not files:
        raise HTTPException(status_code=400, detail="未上传文件")

    resolved_prompt = prompt
    if prompt_id:
        p = get_config_service().get_prompt_by_id(prompt_id)
        if not p:
            raise HTTPException(status_code=404, detail="提示词不存在")
        resolved_prompt = p.get("prompt")

    if not resolved_prompt:
        raise HTTPException(status_code=400, detail="prompt 或 prompt_id 必填")

    tmp_dir = Path(tempfile.mkdtemp(prefix="api_models_connect_stream_"))
    image_paths: list[Path] = []
    try:
        for f in files:
            name = safe_filename(f.filename or "upload")
            dst = tmp_dir / name
            dst.write_bytes(await f.read())
            image_paths.append(dst)
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    q: "queue.Queue[dict | None]" = queue.Queue()

    def emit(ev: dict) -> None:
        q.put(ev)

    def worker() -> None:
        from backend.core.config_loader import get_model, get_provider
        from backend.core.local.cloud_processor import process_images_with_cloud_api
        from backend.core.local.result_handler import get_latest_output_file_path

        processor = get_processor()
        session_dir: Optional[Path] = None
        try:
            session_dir = processor._prepare_session_dir(image_paths)

            provider_cfg = get_provider(provider)
            model_cfg = get_model(provider, model)

            model_name = model_cfg["name"]
            model_info = model_cfg.get("info")
            api_base_url = model_cfg.get("api_base_url")
            provider_defaults = (
                provider_cfg.get("info", {}).get("defaults", {})
                if isinstance(provider_cfg.get("info"), dict)
                else {}
            )
            env_key = model_cfg.get("env_key") or provider_defaults.get("env_key", "API_KEY")

            emit(
                {
                    "event": "run_start",
                    "provider": provider,
                    "model": model,
                    "model_name": model_name,
                    "api_key_env": env_key,
                    "api_base_url": api_base_url,
                    "mode": "streaming",
                }
            )

            success_count, fail_count, output_dir = process_images_with_cloud_api(
                model_name=model_name,
                model_info=model_info,
                input_dir=str(session_dir),
                prompt=resolved_prompt,
                request_delay=request_delay,
                max_retries=max_retries,
                retry_delay=retry_delay,
                api_base_url=api_base_url,
                timeout=timeout,
                enable_compression=enable_compression,
                verbose=False,
                max_workers=max_workers,
                api_key_env=env_key,
                use_streaming=True,
                enable_streaming_print=False,
                emit=emit,
            )

            summary_data: dict = {}
            per_image_payloads: list[dict] = []
            summary_path = output_dir / "run_summary.json"
            if summary_path.is_file():
                summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
                summary_data.setdefault("output_dir", str(output_dir.resolve()))
                for record in summary_data.get("images", []) or []:
                    image_name = record.get("image_name") or ""
                    image_stem = Path(image_name).stem if image_name else ""
                    latest_output = (
                        get_latest_output_file_path(output_dir, image_stem, extension=".json")
                        if image_stem
                        else None
                    )
                    if latest_output:
                        record["output_file"] = str(latest_output)

                    output_file = record.get("output_file")
                    if output_file:
                        payload_path = Path(output_file)
                        if payload_path.is_file():
                            try:
                                payload = json.loads(payload_path.read_text(encoding="utf-8"))
                                payload["_output_file"] = str(payload_path)
                                per_image_payloads.append(payload)
                            except json.JSONDecodeError:
                                continue

            result = {"summary": summary_data, "results": per_image_payloads}

            try:
                totals = summary_data.get("totals", {}) if isinstance(summary_data, dict) else {}
                get_config_service().add_task_record(
                    provider=provider,
                    model=model,
                    file_count=int(totals.get("all") or len(image_paths)),
                    success_count=int(totals.get("success") or success_count),
                    failed_count=int(totals.get("failed") or fail_count),
                    output_dir=summary_data.get("output_dir"),
                )
            except Exception:
                pass

            emit({"event": "done", "result": result})
        except Exception as e:
            emit({"event": "fatal", "error": str(e)})
        finally:
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                pass
            if session_dir is not None:
                try:
                    shutil.rmtree(session_dir, ignore_errors=True)
                except Exception:
                    pass
            q.put(None)

    threading.Thread(target=worker, daemon=True).start()

    def iter_events():
        while True:
            ev = q.get()
            if ev is None:
                break
            yield (json.dumps(ev, ensure_ascii=False) + "\n").encode("utf-8")

    return StreamingResponse(iter_events(), media_type="application/x-ndjson; charset=utf-8")
