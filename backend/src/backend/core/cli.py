"""
命令行入口 (CLI)

- 提供多云视觉/文本处理的统一命令行参数接口
- 支持：
  - 直接通过 --provider / --model 指定厂商与模型
  - 使用 --select 交互式选择厂商与模型
- 主要依赖：
  - src.config_loader.PROVIDERS: 从 config/models.yml 读取厂商与模型列表
  - src.processor.run_pipeline: 执行实际的图片批处理与模型调用
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from backend.core.config import (
    DEFAULT_INPUT_DIR,
    DEFAULT_PROMPT,
    DEFAULT_MAX_IMAGE_SIZE,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_REQUEST_DELAY,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_MAX_WORKERS,
    console,
)
from backend.core.config_loader import get_providers
from backend.core.processor import run_pipeline
from backend.util import project_root as get_project_root

DEFAULT_PROVIDER = "doubao"
DEFAULT_MODEL = "doubao-seed-1-6-vision-250815"

# 记录上次选择的厂商和模型
LAST_CHOICE_FILE = get_project_root() / "config" / "last_choice.json"


def load_last_choice() -> tuple[str | None, str | None]:
    """从 config/last_choice.json 读取上次选择的厂商和模型。"""
    if not LAST_CHOICE_FILE.is_file():
        return None, None
    try:
        data = json.loads(LAST_CHOICE_FILE.read_text(encoding="utf-8"))
        return data.get("provider"), data.get("model")
    except Exception:
        return None, None


def save_last_choice(provider_key: str, model_key: str) -> None:
    """将本次选择的厂商和模型写入 config/last_choice.json。"""
    try:
        LAST_CHOICE_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, str] = {}
        if LAST_CHOICE_FILE.is_file():
            try:
                existing = json.loads(LAST_CHOICE_FILE.read_text(encoding="utf-8"))
                if isinstance(existing, dict):
                    payload.update(existing)
            except Exception:
                payload = {}
        payload["provider"] = provider_key
        payload["model"] = model_key
        LAST_CHOICE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # 写失败不影响主流程，静默忽略
        pass


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="多云视觉抽取客户端（精简版入口）")
    p.add_argument("--provider", default=DEFAULT_PROVIDER, help="厂商键，例如 doubao/aliyun/tencent/baidu")
    p.add_argument("--model", default=DEFAULT_MODEL, help="模型键，见各厂商模型池")
    p.add_argument("--input", dest="input_dir", default=DEFAULT_INPUT_DIR, help="输入图片文件夹")
    p.add_argument("--prompt", default=None, help="提示词（不填则使用全局默认提示词）")
    p.add_argument("--max-image-size", nargs=2, type=int, metavar=("W", "H"), default=DEFAULT_MAX_IMAGE_SIZE,
                   help="最大图片尺寸")
    p.add_argument("--max-file-size-mb", type=int, default=DEFAULT_MAX_FILE_SIZE_MB, help="单图最大文件大小(MB)")
    p.add_argument("--request-delay", type=float, default=DEFAULT_REQUEST_DELAY, help="请求间隔秒")
    p.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES, help="最大重试次数")
    p.add_argument("--retry-delay", type=float, default=DEFAULT_RETRY_DELAY, help="重试间隔秒")
    p.add_argument("--disable-compression", action="store_true", help="禁用图片压缩")
    p.add_argument("--no-verbose", action="store_true", help="关闭详细日志")
    p.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS, help="并发线程数，1为串行")
    p.add_argument("--select", action="store_true", help="运行时交互选择厂商与模型")
    p.add_argument("--api-base", dest="api_base", default=None, help="覆盖模型/厂商默认的 API Base URL")
    p.add_argument("--timeout", type=float, default=60.0, help="请求超时秒数")
    p.add_argument("--check-env", action="store_true", help="检查当前环境支持的模型类型")
    return p


def main(argv: Optional[list[str]] = None) -> None:
    p = build_parser()
    args = p.parse_args(argv)

    # 添加环境检测选项
    if hasattr(args, 'check_env') and args.check_env:
        console.banner("\n环境检测")
        console.info("请运行以下命令进行详细环境检测：")
        console.info("  本地环境: python check_local.py")
        console.info("  云服务器: python check_cloud.py")
        return

    provider_key = args.provider
    model_key = args.model

    # 读取上次选择
    last_provider, last_model = load_last_choice()

    if args.select:
        # 构建展开后的 "厂商-模型" 列表
        # entries: [(provider_key, model_key, display_str), ...]
        entries: list[tuple[str, str, str]] = []
        index = 1
        providers = get_providers()
        for p_key, provider in providers.items():
            info = provider["info"]
            model_pool = provider["model_pool"]

            # 分组标题
            if entries:
                entries.append(("", "", "-" * 55))
            entries.append(("", "", f"[{info['display_name']}] {p_key}"))

            for m_key, m_info in model_pool.items():
                mark = ""
                if last_provider == p_key and last_model == m_key:
                    mark = "  [上次选择]"
                display = f"{index}. {m_key}{mark}"
                entries.append((p_key, m_key, display))
                index += 1

        # 打印列表（彩色）
        console.banner("\n================ 选择模型 (Provider-Model) ================\n")
        for p_key, m_key, display in entries:
            if not p_key and not m_key:
                # 纯分隔行或标题
                if display.startswith("-"):
                    console.detail(display)
                else:
                    console.title(display)
            else:
                if "[上次选择]" in display:
                    console.success(display)
                else:
                    console.info(display)

        # 构建真正可选的 (provider, model) 列表（去掉分隔行）
        choices: list[tuple[str, str]] = [
            (p_key, m_key) for (p_key, m_key, display) in entries if p_key and m_key
        ]

        # 计算默认索引（上次选择，否则第 1 个）
        default_index = 1
        if last_provider and last_model:
            for idx, (p_key, m_key) in enumerate(choices, 1):
                if p_key == last_provider and m_key == last_model:
                    default_index = idx
                    break

        # 交互选择
        while True:
            sel = input(f"\n请输入序号(回车默认 {default_index}): ").strip()
            if not sel:
                provider_key, model_key = choices[default_index - 1]
                break
            if sel.isdigit() and 1 <= int(sel) <= len(choices):
                provider_key, model_key = choices[int(sel) - 1]
                break
            print("无效输入，请重试。")

        # 记住本次选择
        save_last_choice(provider_key, model_key)

    run_pipeline(
        provider_key=provider_key,
        model_key=model_key,
        input_dir=args.input_dir,
        prompt=args.prompt or DEFAULT_PROMPT,
        max_image_size=tuple(args.max_image_size),
        max_file_size_mb=args.max_file_size_mb,
        request_delay=args.request_delay,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        api_base_url_override=args.api_base,
        timeout=args.timeout,
        enable_compression=not args.disable_compression,
        verbose=not args.no_verbose,
        max_workers=args.max_workers,
    )


if __name__ == "__main__":
    main()
