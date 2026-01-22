"""
云API处理模块
处理云端API模型的图片批处理逻辑

改造说明（streaming + 精确计时 + JSON容错）：
- 使用 stream=True 实现真实流式输出
- 精确计时：TTFT / 生成 / 解析 / 保存 / 全链路
- JSON 容错提取与校验
- 失败时保存 .txt 备份
"""
from __future__ import annotations

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from backend.core.config import (
    console, with_icon,
    DEFAULT_INPUT_DIR, DEFAULT_PROMPT, DEFAULT_MAX_IMAGE_SIZE,
    DEFAULT_MAX_FILE_SIZE_MB, DEFAULT_REQUEST_DELAY, DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY, DEFAULT_ENABLE_COMPRESSION, DEFAULT_VERBOSE, DEFAULT_MAX_WORKERS,
)
from backend.core.local.api_client import get_rate_limiter, get_client_pool
from backend.core.local.image_utils import get_image_url, get_image_files
from backend.core.local.result_handler import (
    get_output_file_path, save_result,
)
from backend.util import project_root as get_project_root


def _preprocess_image(
        image_path: Path,
        max_image_size: tuple[int, int],
        max_file_size_mb: int,
        enable_compression: bool,
        verbose: bool,
) -> str:
    """预处理图片，包括压缩和编码"""
    return get_image_url(
        image_path, max_image_size, max_file_size_mb,
        enable_compression, verbose=verbose
    )


def _extract_json_from_text(raw_text: str) -> tuple[Any, bool, str]:
    """
    从模型输出中容错提取 JSON
    
    返回: (parsed_json, is_valid, error_reason)
    - 成功: (json_obj, True, "")
    - 失败: (None, False, "错误原因")
    """
    if not raw_text or not raw_text.strip():
        return None, False, "empty_response"
    
    stripped = raw_text.strip()
    candidates = []
    
    # 1. 尝试直接解析
    candidates.append(stripped)
    
    # 2. 提取 ```json codeblock
    if "```" in stripped:
        # 匹配 ```json ... ``` 或 ``` ... ```
        codeblock_pattern = r"```(?:json)?\s*([\s\S]*?)```"
        matches = re.findall(codeblock_pattern, stripped, re.IGNORECASE)
        for match in matches:
            candidate = match.strip()
            if candidate:
                candidates.append(candidate)
    
    # 3. 提取最外层 {} 对象
    brace_match = re.search(r"\{[\s\S]*\}", stripped)
    if brace_match:
        candidates.append(brace_match.group(0))
    
    # 4. 提取最外层 [] 数组
    bracket_match = re.search(r"\[[\s\S]*\]", stripped)
    if bracket_match:
        candidates.append(bracket_match.group(0))
    
    # 尝试解析每个候选
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            return parsed, True, ""
        except json.JSONDecodeError:
            continue
    
    return None, False, f"no_valid_json_found (tried {len(candidates)} candidates)"


def _save_backup_txt(output_dir: Path, image_stem: str, full_text: str) -> Path:
    """保存原始输出为 .txt 备份文件"""
    backup_file = output_dir / f"{image_stem}_backup.txt"
    counter = 1
    while backup_file.exists():
        backup_file = output_dir / f"{image_stem}_backup_{counter}.txt"
        counter += 1
    
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    return backup_file


def _process_single_image_streaming(
        image_path: Path,
        idx: int,
        total: int,
        model_name: str,
        model_info: Optional[str],
        prompt: str,
        max_image_size: tuple[int, int],
        max_file_size_mb: int,
        request_delay: float,
        max_retries: int,
        retry_delay: float,
        api_base_url: str,
        timeout: Optional[float],
        enable_compression: bool,
        verbose: bool,
        output_dir: Path,
        api_key: str,
        preprocessed_image_url: Optional[str] = None,
        enable_streaming_print: bool = True,
) -> Dict[str, Any]:
    """
    处理单张图片（真实流式版本）
    
    实现：
    - stream=True 真实流式输出
    - TTFT / 生成 / 解析 / 保存 / 全链路 精确计时
    - JSON 容错提取与校验
    - 失败时保存 .txt 备份
    """
    client = get_client_pool().get_client(api_key, api_base_url, timeout)
    rate_limiter = get_rate_limiter()

    # 保留原有日志
    if verbose:
        console.blank()
        console.title(with_icon("camera", f"[{idx}/{total}] {image_path.name}"))

    output_file = get_output_file_path(output_dir, image_path.stem, extension=".json")
    retry_count = 0
    
    # 计时变量
    t0 = None  # 请求发起时间
    t_first = None  # 第一个 token 到达时间
    t_end_stream = None  # 流式结束时间
    t_parse_end = None  # JSON 解析结束时间
    t_save_end = None  # 保存结束时间
    
    while retry_count <= max_retries:
        try:
            if retry_count > 0 and verbose:
                console.warning(with_icon("retry", f"重试({retry_count}/{max_retries})..."))
                time.sleep(retry_delay)

            # 预处理图片
            preprocess_seconds = 0.0
            if preprocessed_image_url is not None:
                image_url = preprocessed_image_url
            else:
                t_pre = time.perf_counter()
                image_url = _preprocess_image(
                    image_path, max_image_size, max_file_size_mb, enable_compression, verbose=False
                )
                preprocess_seconds = time.perf_counter() - t_pre

            # 构建消息
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }]

            # 等待速率限制
            rate_limiter.wait(api_base_url, request_delay)
            
            # ========== 真实流式调用 ==========
            t0 = time.perf_counter()
            
            stream = client.chat.completions.create(
                model=model_name,
                messages=messages,
                stream=True  # 开启真实流式
            )
            
            full_text = ""
            char_count = 0
            t_first = None
            
            # 流式接收并打印
            for chunk in stream:
                # 提取 delta 内容
                delta_content = ""
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and hasattr(delta, "content") and delta.content:
                        delta_content = delta.content
                
                if delta_content:
                    # 记录 TTFT（第一个 token 到达时间）
                    if t_first is None:
                        t_first = time.perf_counter()
                        ttft = t_first - t0
                        print(f"\n[TIME] TTFT={ttft:.3f}s", flush=True)
                    
                    # 打字机效果输出
                    if enable_streaming_print:
                        print(delta_content, end="", flush=True)
                    
                    full_text += delta_content
                    char_count += len(delta_content)
            
            # 流式结束
            t_end_stream = time.perf_counter()
            
            # 如果没有收到任何内容
            if t_first is None:
                t_first = t_end_stream
                print(f"\n[TIME] TTFT=N/A (no content)", flush=True)
            
            # 打印流式结束统计
            gen_time = t_end_stream - t_first
            total_stream_time = t_end_stream - t0
            print(f"\n[TIME] gen={gen_time:.3f}s total={total_stream_time:.3f}s chars={char_count}", flush=True)
            
            # ========== JSON 后处理 ==========
            t_parse_start = time.perf_counter()
            
            parsed_json, is_valid, error_reason = _extract_json_from_text(full_text)
            
            t_parse_end = time.perf_counter()
            parse_seconds = t_parse_end - t_parse_start
            
            if is_valid:
                print(f"[JSON] parse={parse_seconds:.3f}s valid=True", flush=True)
            else:
                print(f"[JSON] parse={parse_seconds:.3f}s valid=False reason={error_reason}", flush=True)
            
            # ========== 保存结果 ==========
            t_save_start = time.perf_counter()
            
            if is_valid:
                # JSON 解析成功，正常保存
                save_result(
                    output_file, image_path, model_name, model_info, prompt,
                    result_json=parsed_json, raw_response=full_text,
                )
                t_save_end = time.perf_counter()
                save_seconds = t_save_end - t_save_start
                print(f"[SAVE] save={save_seconds:.3f}s path={output_file}", flush=True)
                
                # 保留原有日志
                if verbose:
                    console.success(with_icon("save", f"已保存 {output_file.name}"))
            else:
                # JSON 解析失败，保存备份
                print(f"[ERR] JSON_PARSE_FAILED reason={error_reason}", flush=True)
                
                # 保存 .txt 备份
                backup_file = _save_backup_txt(output_dir, image_path.stem, full_text)
                
                # 同时保存带错误信息的 JSON
                save_result(
                    output_file, image_path, model_name, model_info, prompt,
                    error_msg=f"JSON解析失败: {error_reason}",
                    raw_response=full_text,
                )
                
                t_save_end = time.perf_counter()
                save_seconds = t_save_end - t_save_start
                print(f"[SAVE] save={save_seconds:.3f}s backup={backup_file}", flush=True)
                
                if verbose:
                    console.warning(with_icon("warning", f"JSON解析失败，已保存备份: {backup_file.name}"))
            
            # ========== 全链路耗时 ==========
            all_time = t_save_end - t0
            print(f"[TIME] all={all_time:.3f}s", flush=True)
            
            # 返回结果
            return {
                "index": idx, 
                "image_name": image_path.name,
                "status": "success" if is_valid else "json_parse_failed",
                "output_file": str(output_file), 
                "retries": retry_count,
                "json_valid": is_valid,
                "timings": {
                    "preprocess_seconds": round(preprocess_seconds, 4),
                    "ttft_seconds": round((t_first - t0) if t_first else 0, 4),
                    "gen_seconds": round(gen_time, 4),
                    "stream_total_seconds": round(total_stream_time, 4),
                    "parse_seconds": round(parse_seconds, 4),
                    "save_seconds": round(save_seconds, 4),
                    "all_seconds": round(all_time, 4),
                },
                "char_count": char_count,
            }

        except Exception as e:
            retry_count += 1
            error_msg = str(e)
            
            # 计算已完成阶段的耗时
            current_time = time.perf_counter()
            elapsed = current_time - t0 if t0 else 0
            
            print(f"[ERR] EXCEPTION retry={retry_count}/{max_retries} elapsed={elapsed:.3f}s error={error_msg}", flush=True)
            
            if verbose:
                console.error(with_icon("error", f"错误: {error_msg}"))
            
            if retry_count > max_retries:
                # 保存错误信息
                t_save_start = time.perf_counter()
                
                # 如果有部分输出，保存备份
                if 'full_text' in locals() and full_text:
                    backup_file = _save_backup_txt(output_dir, image_path.stem, full_text)
                    print(f"[SAVE] backup={backup_file}", flush=True)
                
                save_result(
                    output_file, image_path, model_name, model_info, prompt,
                    error_msg=error_msg, raw_response=locals().get("full_text"),
                )
                
                t_save_end = time.perf_counter()
                save_seconds = t_save_end - t_save_start
                print(f"[SAVE] error_save={save_seconds:.3f}s path={output_file}", flush=True)
                
                all_time = t_save_end - t0 if t0 else elapsed
                print(f"[TIME] all={all_time:.3f}s (failed)", flush=True)
                
                return {
                    "index": idx, 
                    "image_name": image_path.name,
                    "status": "failed", 
                    "output_file": str(output_file), 
                    "error": error_msg, 
                    "retries": retry_count - 1,
                    "timings": {
                        "elapsed_before_fail": round(elapsed, 4),
                    },
                }
            
            time.sleep(retry_delay)

    # 不应该到达这里
    return {
        "index": idx, 
        "image_name": image_path.name, 
        "status": "failed",
        "output_file": None, 
        "error": "未知错误", 
        "retries": max_retries
    }


# 保留原有的非流式版本作为备用
def _process_single_image(
        image_path: Path,
        idx: int,
        total: int,
        model_name: str,
        model_info: Optional[str],
        prompt: str,
        max_image_size: tuple[int, int],
        max_file_size_mb: int,
        request_delay: float,
        max_retries: int,
        retry_delay: float,
        api_base_url: str,
        timeout: Optional[float],
        enable_compression: bool,
        verbose: bool,
        output_dir: Path,
        api_key: str,
        preprocessed_image_url: Optional[str] = None,
        use_streaming: bool = True,
) -> Dict[str, Any]:
    """
    处理单张图片（入口函数）
    
    默认使用流式版本，可通过 use_streaming=False 切换到非流式
    """
    if use_streaming:
        return _process_single_image_streaming(
            image_path=image_path,
            idx=idx,
            total=total,
            model_name=model_name,
            model_info=model_info,
            prompt=prompt,
            max_image_size=max_image_size,
            max_file_size_mb=max_file_size_mb,
            request_delay=request_delay,
            max_retries=max_retries,
            retry_delay=retry_delay,
            api_base_url=api_base_url,
            timeout=timeout,
            enable_compression=enable_compression,
            verbose=verbose,
            output_dir=output_dir,
            api_key=api_key,
            preprocessed_image_url=preprocessed_image_url,
            enable_streaming_print=True,
        )
    
    # 非流式版本（保留原有逻辑）
    from backend.core.local.result_handler import extract_text_from_message, parse_json_from_model_output
    
    client = get_client_pool().get_client(api_key, api_base_url, timeout)
    rate_limiter = get_rate_limiter()

    if verbose:
        console.blank()
        console.title(with_icon("camera", f"[{idx}/{total}] {image_path.name}"))

    output_file = get_output_file_path(output_dir, image_path.stem, extension=".json")
    retry_count = 0

    while retry_count <= max_retries:
        try:
            if retry_count > 0 and verbose:
                console.warning(with_icon("retry", f"重试({retry_count}/{max_retries})..."))
                time.sleep(retry_delay)

            preprocess_seconds = 0.0
            if preprocessed_image_url is not None:
                image_url = preprocessed_image_url
            else:
                t0 = time.perf_counter()
                image_url = _preprocess_image(
                    image_path, max_image_size, max_file_size_mb, enable_compression, verbose=False
                )
                preprocess_seconds = time.perf_counter() - t0

            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }]

            rate_limiter.wait(api_base_url, request_delay)
            t_api = time.perf_counter()
            completion = client.chat.completions.create(model=model_name, messages=messages)
            api_seconds = time.perf_counter() - t_api
            result = completion.choices[0].message
            raw_text = extract_text_from_message(result)
            t_parse = time.perf_counter()
            structured_json = parse_json_from_model_output(raw_text)
            parse_seconds = time.perf_counter() - t_parse

            t_save = time.perf_counter()
            save_result(
                output_file, image_path, model_name, model_info, prompt,
                result_json=structured_json, raw_response=raw_text,
            )
            save_seconds = time.perf_counter() - t_save

            if verbose:
                console.success(with_icon("save", f"已保存 {output_file.name}"))

            return {
                "index": idx, "image_name": image_path.name,
                "status": "success", "output_file": str(output_file), "retries": retry_count,
                "timings": {
                    "preprocess_seconds": round(preprocess_seconds, 4),
                    "api_seconds": round(api_seconds, 4),
                    "parse_seconds": round(parse_seconds, 4),
                    "save_seconds": round(save_seconds, 4),
                },
            }

        except Exception as e:
            retry_count += 1
            error_msg = str(e)
            if verbose:
                console.error(with_icon("error", f"错误: {error_msg}"))
            if retry_count > max_retries:
                save_result(
                    output_file, image_path, model_name, model_info, prompt,
                    error_msg=error_msg, raw_response=locals().get("raw_text"),
                )
                return {
                    "index": idx, "image_name": image_path.name,
                    "status": "failed", "output_file": None, "error": error_msg, "retries": retry_count - 1,
                }
            time.sleep(retry_delay)

    return {"index": idx, "image_name": image_path.name, "status": "failed",
            "output_file": None, "error": "未知错误", "retries": max_retries}


def process_images_with_cloud_api(
        *,
        model_name: str,
        model_info: Optional[str] = None,
        input_dir: str = DEFAULT_INPUT_DIR,
        prompt: str = DEFAULT_PROMPT,
        max_image_size=DEFAULT_MAX_IMAGE_SIZE,
        max_file_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB,
        request_delay: float = DEFAULT_REQUEST_DELAY,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        api_base_url: Optional[str] = None,
        timeout: Optional[float] = 60.0,
        enable_compression: bool = DEFAULT_ENABLE_COMPRESSION,
        verbose: bool = DEFAULT_VERBOSE,
        max_workers: int = DEFAULT_MAX_WORKERS,
        api_key_env: Optional[str] = None,
        use_streaming: bool = True,
):
    """对输入文件夹中的图片逐张调用云API模型，保存结果并返回统计信息"""
    project_root = get_project_root()

    # 输出目录
    base_output_dir = project_root / "data" / "outputs"
    base_output_dir.mkdir(parents=True, exist_ok=True)
    model_folder_name = model_name.replace("/", "-").replace(":", "-")
    output_dir = base_output_dir / model_folder_name
    output_dir.mkdir(exist_ok=True)

    # 输入目录
    input_path_obj = Path(input_dir)
    input_dir_path = input_path_obj if input_path_obj.is_absolute() else project_root / input_path_obj

    if verbose:
        console.info(with_icon("output", f"输出文件夹: {output_dir}"))

    if not api_key_env:
        raise ValueError("API key env name is missing (set api_key_env).")
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise ValueError(f"Environment variable {api_key_env} is required for authentication.")
    if not api_base_url:
        raise ValueError("API Base URL is missing; configure it in models.yml or via --api-base.")

    if verbose:
        console.detail(with_icon("info", f"使用环境变量键: {api_key_env}"))
        console.detail(with_icon("info", f"API Base: {api_base_url}"))
        if use_streaming:
            console.detail(with_icon("info", "模式: 流式输出 (streaming)"))

    image_files = get_image_files(input_dir_path, project_root)
    if verbose:
        console.info(with_icon("image_list", f"找到 {len(image_files)} 张图片"))
        console.blank()

    start_time = datetime.now()
    run_records: List[Dict[str, Any]] = []
    success_count = 0
    fail_count = 0
    total = len(image_files)

    # 并行预处理所有图片
    preprocessed_images = {}
    if max_workers > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_preprocess_image, img, max_image_size, max_file_size_mb, enable_compression,
                                False): img
                for img in image_files
            }
            for future in futures:
                img = futures[future]
                try:
                    preprocessed_images[img] = future.result()
                except Exception:
                    preprocessed_images[img] = None
    else:
        for img in image_files:
            try:
                preprocessed_images[img] = _preprocess_image(img, max_image_size, max_file_size_mb, enable_compression,
                                                             False)
            except Exception:
                preprocessed_images[img] = None

    # 处理图片（流式模式下建议串行，避免输出混乱）
    if use_streaming:
        # 流式模式：串行处理，保证输出清晰
        for idx, img in enumerate(image_files, 1):
            result = _process_single_image(
                img, idx, total, model_name, model_info, prompt,
                max_image_size, max_file_size_mb, request_delay, max_retries, retry_delay,
                api_base_url, timeout, enable_compression, verbose, output_dir, api_key,
                preprocessed_images[img], use_streaming=True
            )
            run_records.append(result)
            if result["status"] == "success":
                success_count += 1
            else:
                fail_count += 1
    elif max_workers > 1:
        # 非流式模式：可并行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    _process_single_image, img, idx, total, model_name, model_info, prompt,
                    max_image_size, max_file_size_mb, request_delay, max_retries, retry_delay,
                    api_base_url, timeout, enable_compression, verbose, output_dir, api_key,
                    preprocessed_images[img], False
                )
                for idx, img in enumerate(image_files, 1)
            ]
            for future in futures:
                result = future.result()
                run_records.append(result)
                if result["status"] == "success":
                    success_count += 1
                else:
                    fail_count += 1
    else:
        for idx, img in enumerate(image_files, 1):
            result = _process_single_image(
                img, idx, total, model_name, model_info, prompt,
                max_image_size, max_file_size_mb, request_delay, max_retries, retry_delay,
                api_base_url, timeout, enable_compression, verbose, output_dir, api_key,
                preprocessed_images[img], use_streaming=False
            )
            run_records.append(result)
            if result["status"] == "success":
                success_count += 1
            else:
                fail_count += 1

    end_time = datetime.now()
    elapsed_seconds = (end_time - start_time).total_seconds()
    avg_per_image = elapsed_seconds / total if total > 0 else 0.0

    if verbose:
        console.blank()
        console.banner("=" * 60)
        console.success(with_icon("success", "处理完成！"))
        console.info(with_icon("success", f"成功: {success_count} 张"))
        console.info(with_icon("warning", f"失败: {fail_count} 张"))
        console.info(with_icon("info", f"总耗时: {elapsed_seconds:.2f} 秒，平均每张: {avg_per_image:.2f} 秒"))
        console.info(with_icon("output", f"结果保存在: {output_dir.resolve()}"))
        console.banner("=" * 60)

    summary = {
        "model_name": model_name, "model_info": model_info, "prompt": prompt,
        "run_started_at": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "run_finished_at": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": elapsed_seconds,
        "avg_seconds_per_image": avg_per_image,
        "max_workers": max_workers,
        "use_streaming": use_streaming,
        "request_delay": request_delay,
        "max_retries": max_retries,
        "retry_delay": retry_delay,
        "enable_compression": enable_compression,
        "max_image_size": list(max_image_size),
        "max_file_size_mb": max_file_size_mb,
        "input_dir": str(input_dir_path.resolve()),
        "output_dir": str(output_dir.resolve()),
        "totals": {"success": success_count, "failed": fail_count, "all": total},
        "images": run_records,
    }
    summary_path = output_dir / "run_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return success_count, fail_count, output_dir
