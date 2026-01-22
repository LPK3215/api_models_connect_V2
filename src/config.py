"""
合并配置与日志工具
- 默认参数常量
- 彩色控制台日志
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict

import yaml

# =====================
# 加载环境变量（.env文件）
# =====================
try:
    from dotenv import load_dotenv

    # 加载项目根目录的.env文件
    _project_root = Path(__file__).resolve().parent.parent
    _env_file = _project_root / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    # 如果没有安装python-dotenv，跳过（使用系统环境变量）
    pass


# =====================
# 输出编码（Windows 兼容）
# =====================
def _ensure_utf8_output() -> None:
    """尽量避免 Windows 控制台(GBK)因 Emoji/特殊字符导致的 UnicodeEncodeError。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                encoding = (getattr(stream, "encoding", "") or "").lower()
                if encoding and encoding != "utf-8":
                    stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


_ensure_utf8_output()

# =====================
# 默认配置
# =====================
DEFAULT_INPUT_DIR = "data/inputs"


def _load_default_prompt() -> str:
    """从 config/prompts/default.yml 加载默认提示词，文件缺失或读取失败时使用内置提示词。"""
    project_root = Path(__file__).resolve().parent.parent
    prompt_path = project_root / "config" / "prompts" / "default.yml"

    # 内置默认提示词作为后备
    fallback_prompt = """你是一名专业的信息抽取助手，请从图像中识别全部可读文字和结构，并整理为结构化 JSON。
输出要求：
1. 仅输出合法 JSON（不包含额外说明、Markdown 代码块或多余字符）。
2. JSON 顶层需包含字段：
   - "document_title": 字符串或 null
   - "primary_language": 主要语言（如 "zh"、"en"）
   - "overall_summary": 对整体内容的简洁总结
   - "sections": 列表，元素为对象，需包含 "heading"（可为 null）、"summary"、"key_points"（字符串数组）、"raw_text"
   - "tables": 列表，元素为对象，需包含 "title"、"headers"（字符串数组）、"rows"（二维数组）、"notes"（可为 null）；若无表格请返回空列表
   - "warnings": 列表，收集安全警示、注意事项等关键信息；若无则空列表
   - "figures": 列表，描述图片或图标内容与含义
   - "extraction_confidence": "high"、"medium" 或 "low"
3. 凡是识别到的条目、表格行、注意事项都要完整保留；遇到无法识别的内容可在对应字段填 null 或说明"疑似缺失"。
4. 所有字符串使用双引号，确保 JSON 可直接解析。
5. 对表格、列表等结构化内容，请以嵌套数组/对象形式表达。"""

    if not prompt_path.is_file():
        return fallback_prompt.strip()

    try:
        raw = prompt_path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        if isinstance(data, dict) and "prompt" in data and isinstance(data["prompt"], str):
            return data["prompt"].strip()
        return fallback_prompt.strip()
    except Exception:
        return fallback_prompt.strip()


DEFAULT_PROMPT = _load_default_prompt()

DEFAULT_MAX_IMAGE_SIZE = (1024, 1024)
DEFAULT_MAX_FILE_SIZE_MB = 1
DEFAULT_REQUEST_DELAY = 0
DEFAULT_MAX_RETRIES = 0
DEFAULT_RETRY_DELAY = 5
DEFAULT_ENABLE_COMPRESSION = True
DEFAULT_VERBOSE = True
DEFAULT_MAX_WORKERS = 1

# =====================
# 彩色控制台
# =====================
try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)
    COLOR_AVAILABLE = True
except Exception:  # 降级
    COLOR_AVAILABLE = False
    Fore = Style = None  # type: ignore


def _apply_color(text: str, color: Optional[str]) -> str:
    if COLOR_AVAILABLE and color:
        return f"{color}{text}{Style.RESET_ALL}"
    return text


class ConsoleLogger:
    def __init__(self) -> None:
        if not COLOR_AVAILABLE:
            print("⚠️ 未检测到 colorama，输出为普通文本。可运行 'pip install colorama' 获得彩色提示。")

    def banner(self, text: str) -> None:
        print(_apply_color(text, Fore.MAGENTA if COLOR_AVAILABLE else None))

    def title(self, text: str) -> None:
        print(_apply_color(text, Fore.CYAN if COLOR_AVAILABLE else None))

    def info(self, text: str) -> None:
        print(_apply_color(text, Fore.LIGHTCYAN_EX if COLOR_AVAILABLE else None))

    def detail(self, text: str) -> None:
        # 更人眼易读，避免灰色
        print(_apply_color(text, Fore.WHITE if COLOR_AVAILABLE else None))

    def success(self, text: str) -> None:
        print(_apply_color(text, Fore.GREEN if COLOR_AVAILABLE else None))

    def warning(self, text: str) -> None:
        print(_apply_color(text, Fore.YELLOW if COLOR_AVAILABLE else None))

    def error(self, text: str) -> None:
        print(_apply_color(text, Fore.RED if COLOR_AVAILABLE else None))

    def blank(self) -> None:
        print()

    def spinner(self, text: str) -> "SpinnerHandle":
        sys.stdout.write(_apply_color(text, Fore.CYAN if COLOR_AVAILABLE else None))
        sys.stdout.flush()
        return SpinnerHandle()


@dataclass
class SpinnerHandle:
    def done(self, suffix: str = " ✓") -> None:
        sys.stdout.write(_apply_color(suffix, Fore.GREEN if COLOR_AVAILABLE else None))
        sys.stdout.write("\n")
        sys.stdout.flush()


ICONS: Dict[str, str] = {
    "rocket": "🚀",
    "provider": "🏢",
    "model": "🤖",
    "info": "ℹ️",
    "docs": "📚",
    "folder": "📁",
    "input": "🗂️",
    "output": "📦",
    "camera": "📸",
    "image_list": "🖼️",
    "api": "⏱️",
    "save": "💾",
    "success": "✅",
    "warning": "⚠️",
    "error": "❌",
    "retry": "🔁",
}


def with_icon(name: str, text: str) -> str:
    icon = ICONS.get(name, "")
    return f"{icon} {text}" if icon else text


console = ConsoleLogger()

__all__ = [
    # defaults
    "DEFAULT_INPUT_DIR",
    "DEFAULT_PROMPT",
    "DEFAULT_MAX_IMAGE_SIZE",
    "DEFAULT_MAX_FILE_SIZE_MB",
    "DEFAULT_REQUEST_DELAY",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_RETRY_DELAY",
    "DEFAULT_ENABLE_COMPRESSION",
    "DEFAULT_VERBOSE",
    "DEFAULT_MAX_WORKERS",
    # logger
    "console",
    "ICONS",
    "with_icon",
]
