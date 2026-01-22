"""
结果处理模块
包含JSON解析、结果保存等功能
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


def extract_text_from_message(message: Any) -> str:
    """从模型返回的消息中提取文本内容"""
    if not message:
        return ""
    content = getattr(message, "content", "")
    if isinstance(content, list):
        text_fragments = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and item.get("text"):
                    text_fragments.append(item["text"])
            elif isinstance(item, str):
                text_fragments.append(item)
        return "".join(text_fragments).strip()
    if content is None:
        return ""
    return str(content).strip()


def parse_json_from_model_output(raw_text: str) -> Dict[str, Any] | List[Any] | Any:
    """从模型返回的原始文本中解析出JSON数据"""
    if not raw_text:
        raise ValueError("模型未返回任何内容，请检查提示词和模型配置")

    stripped = raw_text.strip()
    candidates = [stripped]

    if "```" in stripped:
        parts = re.split(r"```(?:json)?", stripped, flags=re.IGNORECASE)
        for part in parts:
            candidate = part.strip().strip("`").strip()
            if candidate:
                candidates.append(candidate)

    brace_match = re.search(r"\{[\s\S]*\}", stripped)
    if brace_match:
        candidates.append(brace_match.group(0))

    bracket_match = re.search(r"\[[\s\S]*\]", stripped)
    if bracket_match:
        candidates.append(bracket_match.group(0))

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    raise ValueError(
        f"模型输出不是合法的JSON数据，请检查提示词是否要求模型返回JSON格式。\n原始输出: {raw_text[:100]}...")


def get_output_file_path(output_dir: Path, image_name: str, extension: str = ".json") -> Path:
    """获取输出文件路径，自动处理重名"""
    output_dir.mkdir(parents=True, exist_ok=True)
    base_filename = f"{image_name}_结果{extension}"
    output_file = output_dir / base_filename

    if output_file.exists():
        counter = 1
        while True:
            numbered_filename = f"{image_name}_结果_{counter}{extension}"
            output_file = output_dir / numbered_filename
            if not output_file.exists():
                break
            counter += 1
    return output_file


def get_latest_output_file_path(output_dir: Path, image_name: str, extension: str = ".json") -> Optional[Path]:
    """获取已存在的最新输出文件路径（用于读取），自动处理编号后缀。

    规则：
    - 匹配 `{image_name}_结果{extension}` 以及 `{image_name}_结果_{n}{extension}`
    - 若存在编号文件，优先返回编号最大的那个；否则返回未编号文件
    - 若不存在匹配文件，返回 None

    健壮性增强：
    - 处理空 image_name
    - 处理特殊字符转义
    - 处理文件系统异常
    """
    if not output_dir or not image_name:
        return None

    try:
        output_dir = Path(output_dir)
        if not output_dir.exists() or not output_dir.is_dir():
            return None
    except (TypeError, OSError):
        return None

    # 转义 image_name 中的正则特殊字符
    escaped_name = re.escape(str(image_name))
    escaped_ext = re.escape(str(extension))
    pattern = re.compile(rf"^{escaped_name}_结果(?:_(\d+))?{escaped_ext}$")

    candidates: List[tuple[int, float, Path]] = []
    try:
        for path in output_dir.iterdir():
            try:
                if not path.is_file():
                    continue
                match = pattern.match(path.name)
                if not match:
                    continue
                counter = int(match.group(1) or 0)
                try:
                    mtime = path.stat().st_mtime
                except OSError:
                    mtime = 0.0
                candidates.append((counter, mtime, path))
            except (OSError, ValueError):
                # 跳过无法访问的文件
                continue
    except (FileNotFoundError, PermissionError, OSError):
        return None

    if not candidates:
        return None

    # 按编号降序，同编号按修改时间降序
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return candidates[0][2]


def save_result(
        output_file: Path,
        image_path: Path,
        model_name: str,
        model_info: Optional[str],
        prompt: str,
        result_json: Optional[Dict[str, Any] | List[Any] | Any] = None,
        error_msg: Optional[str] = None,
        raw_response: Optional[str] = None,
):
    """将处理结果保存到JSON文件中"""
    payload = {
        "image_name": image_path.name,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model_name": model_name,
    }
    context = {
        "image_path": str(image_path),
        "model_info": model_info,
    }
    payload["context"] = context

    if error_msg:
        payload["status"] = "error"
        payload["error"] = {"message": error_msg}
        if raw_response:
            payload["error"]["raw_response"] = raw_response
    else:
        payload["status"] = "success"
        payload["result"] = result_json
        if raw_response and result_json is None:
            payload["raw_model_output"] = raw_response

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
