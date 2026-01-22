"""
处理管线 - 统一入口
调用云端API处理图片
"""
from __future__ import annotations

import errno
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Sequence
from uuid import uuid4

from backend.core.config import (
    console, with_icon,
    DEFAULT_INPUT_DIR, DEFAULT_PROMPT, DEFAULT_MAX_IMAGE_SIZE,
    DEFAULT_MAX_FILE_SIZE_MB, DEFAULT_REQUEST_DELAY, DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY, DEFAULT_ENABLE_COMPRESSION, DEFAULT_VERBOSE,
    DEFAULT_MAX_WORKERS, _load_default_prompt,
)
from backend.core.config_loader import get_provider, get_model
from backend.core.local.result_handler import get_latest_output_file_path
from backend.util import project_root as get_project_root

# 延迟导入处理模块
_cloud_api_processor = None


def _get_cloud_api_processor():
    """获取云API处理器"""
    global _cloud_api_processor
    if _cloud_api_processor is None:
        from backend.core.local.cloud_processor import process_images_with_cloud_api
        _cloud_api_processor = process_images_with_cloud_api
    return _cloud_api_processor


# 兼容旧接口
def process_images_with_model(**kwargs):
    """云API处理"""
    return _get_cloud_api_processor()(**kwargs)


def run_pipeline(
        *,
        provider_key: str,
        model_key: str,
        input_dir: str = DEFAULT_INPUT_DIR,
        prompt: str = DEFAULT_PROMPT,
        max_image_size: tuple[int, int] = DEFAULT_MAX_IMAGE_SIZE,
        max_file_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB,
        request_delay: float = DEFAULT_REQUEST_DELAY,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        api_base_url_override: Optional[str] = None,
        timeout: Optional[float] = 60.0,
        enable_compression: bool = DEFAULT_ENABLE_COMPRESSION,
        verbose: bool = DEFAULT_VERBOSE,
        max_workers: int = DEFAULT_MAX_WORKERS,
        extra_metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """统一入口: 调用云端API处理图片"""
    provider = get_provider(provider_key)
    provider_info = provider["info"]
    model_config = get_model(provider_key, model_key)

    model_name = model_config["name"]
    model_info = model_config["info"]

    resolved_prompt = prompt
    if not resolved_prompt:
        try:
            resolved_prompt = _load_default_prompt()
        except Exception:
            pass
    if not resolved_prompt:
        resolved_prompt = DEFAULT_PROMPT

    api_base_url = api_base_url_override or model_config.get("api_base_url")
    env_key = model_config.get("env_key") or provider_info["defaults"].get("env_key", "API_KEY")

    if not os.environ.get(env_key):
        console.warning(with_icon("warning", f"未检测到环境变量 {env_key}"))

    if verbose:
        console.banner("=" * 60)
        console.title(with_icon("rocket", f"使用模型: {model_name}"))
        console.info(with_icon("model", f"模型介绍: {model_info}"))
        console.info(with_icon("provider", f"平台: {provider_info['display_name']}"))
        console.info(with_icon("input", f"输入文件夹: {input_dir}"))
        console.banner("=" * 60)
        console.blank()

    _get_cloud_api_processor()(
        model_name=model_name, model_info=model_info, input_dir=input_dir,
        prompt=resolved_prompt, max_image_size=max_image_size,
        max_file_size_mb=max_file_size_mb, request_delay=request_delay,
        max_retries=max_retries, retry_delay=retry_delay,
        api_base_url=api_base_url, timeout=timeout,
        enable_compression=enable_compression, verbose=verbose,
        max_workers=max_workers, api_key_env=env_key,
    )


class Processor:
    """包装处理流程，便于Web UI或编程场景复用"""

    def __init__(self, workspace: Optional[Path] = None) -> None:
        self.project_root = get_project_root()
        default_workspace = self.project_root / "data" / "inputs" / "_web_uploads"
        self.workspace = workspace or default_workspace
        self.workspace.mkdir(parents=True, exist_ok=True)

    def _stage_file(self, src_path: Path, destination: Path) -> None:
        """尽量用硬链接/快速复制把文件放入 session 目录，降低 Web 端处理耗时。"""
        try:
            os.link(src_path, destination)
            return
        except OSError as e:
            if e.errno not in (errno.EXDEV, errno.EPERM, errno.EACCES, errno.EEXIST):
                pass
        try:
            shutil.copyfile(src_path, destination)
        except Exception:
            shutil.copy2(src_path, destination)

    def _prepare_session_dir(self, image_paths: Sequence[Path]) -> Path:
        if not image_paths:
            raise ValueError("没有所需处理的图片")
        session_dir = self.workspace / f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}"
        session_dir.mkdir(parents=True, exist_ok=True)
        name_counters: Dict[str, int] = {}
        for src_path in image_paths:
            if not src_path.exists():
                raise FileNotFoundError(f"找不到图片文件: {src_path}")
            stem = src_path.stem
            suffix = src_path.suffix
            candidate = src_path.name
            destination = session_dir / candidate
            counter = name_counters.get(stem, 0)
            while destination.exists():
                counter += 1
                candidate = f"{stem}_{counter}{suffix}"
                destination = session_dir / candidate
            name_counters[stem] = counter
            self._stage_file(src_path, destination)
        return session_dir

    def process(
            self,
            *,
            provider_key: str,
            model_key: str,
            images: Sequence[str | Path],
            prompt: Optional[str] = None,
            max_image_size: tuple[int, int] = DEFAULT_MAX_IMAGE_SIZE,
            max_file_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB,
            request_delay: float = DEFAULT_REQUEST_DELAY,
            max_retries: int = DEFAULT_MAX_RETRIES,
            retry_delay: float = DEFAULT_RETRY_DELAY,
            timeout: Optional[float] = 60.0,
            enable_compression: bool = DEFAULT_ENABLE_COMPRESSION,
            verbose: bool = False,
            max_workers: int = DEFAULT_MAX_WORKERS,
    ) -> Dict[str, Any]:
        """批量处理图片"""
        path_list = [Path(p) if not isinstance(p, Path) else p for p in images]
        session_dir = self._prepare_session_dir(path_list)

        provider = get_provider(provider_key)
        model_config = get_model(provider_key, model_key)

        model_name = model_config["name"]
        model_info = model_config.get("info")
        api_base_url = model_config.get("api_base_url")
        provider_defaults = provider["info"].get("defaults", {}) if isinstance(provider.get("info"), dict) else {}
        env_key = model_config.get("env_key") or provider_defaults.get("env_key", "API_KEY")

        resolved_prompt = prompt or DEFAULT_PROMPT

        summary_data: Dict[str, Any] = {}
        per_image_payloads: List[Dict[str, Any]] = []
        try:
            _, _, output_dir = _get_cloud_api_processor()(
                model_name=model_name, model_info=model_info, input_dir=str(session_dir),
                prompt=resolved_prompt, max_image_size=max_image_size,
                max_file_size_mb=max_file_size_mb, request_delay=request_delay,
                max_retries=max_retries, retry_delay=retry_delay,
                api_base_url=api_base_url, timeout=timeout,
                enable_compression=enable_compression, verbose=verbose,
                max_workers=max_workers, api_key_env=env_key,
            )

            summary_path = output_dir / "run_summary.json"
            if summary_path.is_file():
                summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
                summary_data.setdefault("output_dir", str(output_dir.resolve()))
                for record in summary_data.get("images", []):
                    image_name = record.get("image_name") or ""
                    image_stem = Path(image_name).stem if image_name else ""

                    latest_output = get_latest_output_file_path(output_dir, image_stem,
                                                                extension=".json") if image_stem else None
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

            return {"summary": summary_data, "results": per_image_payloads}
        finally:
            try:
                shutil.rmtree(session_dir, ignore_errors=True)
            except Exception:
                pass
