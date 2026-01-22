"""
图片处理工具模块
包含图片压缩、编码、缓存等功能
"""
from __future__ import annotations

import base64
import gc
import hashlib
import io
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List

from backend.core.config import console

try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


class ImageCache:
    """图片预处理缓存（LRU），避免重复压缩编码相同图片"""

    def __init__(self, max_size: int = 100):
        self._cache: "OrderedDict[str, str]" = OrderedDict()
        self._max_size = max_size

    def _get_cache_key(self, image_path: Path, max_size: tuple, max_file_size_mb: int,
                       enable_compression: bool) -> str:
        """生成缓存键"""
        try:
            stat = image_path.stat()
            file_info = f"{stat.st_mtime}_{stat.st_size}"
        except OSError:
            file_info = str(image_path)

        params = f"{max_size}_{max_file_size_mb}_{enable_compression}"
        cache_key = f"{image_path.name}_{file_info}_{params}"
        return hashlib.md5(cache_key.encode()).hexdigest()

    def get(self, image_path: Path, max_size: tuple, max_file_size_mb: int,
            enable_compression: bool) -> Optional[str]:
        """从缓存获取图片URL（并将其标记为最近使用）"""
        cache_key = self._get_cache_key(image_path, max_size, max_file_size_mb, enable_compression)
        value = self._cache.get(cache_key)
        if value is not None:
            # 标记为最近使用
            self._cache.move_to_end(cache_key, last=True)
        return value

    def put(self, image_path: Path, max_size: tuple, max_file_size_mb: int,
            enable_compression: bool, image_url: str):
        """将图片URL存入缓存，必要时移除最旧条目"""
        cache_key = self._get_cache_key(image_path, max_size, max_file_size_mb, enable_compression)

        if cache_key in self._cache:
            # 更新并标记为最近使用
            self._cache.move_to_end(cache_key, last=True)
            self._cache[cache_key] = image_url
            return

        self._cache[cache_key] = image_url
        if len(self._cache) > self._max_size:
            # 弹出最旧（最少使用）的项
            self._cache.popitem(last=False)

    def clear(self):
        """清空缓存"""
        self._cache.clear()


# 全局缓存实例
_IMAGE_CACHE = ImageCache()


@contextmanager
def memory_efficient_processing(do_collect: bool = False):
    """内存高效处理上下文管理器（默认不强制 GC，避免拖慢处理速度）。"""
    try:
        yield
    finally:
        if do_collect:
            gc.collect()


def compress_image(
        image_path: Path,
        max_size: tuple[int, int] = (1024, 1024),
        max_file_size_mb: int = 1,
        *,
        verbose: bool = True,
) -> tuple[bytes, str]:
    """压缩图片到指定大小"""
    if not HAS_PIL:
        raise ValueError("需要安装 Pillow 才能压缩图片: pip install Pillow")

    is_large_image = False
    with memory_efficient_processing(do_collect=False):
        try:
            with Image.open(image_path) as img:
                original_size = img.size
                file_size_mb = image_path.stat().st_size / (1024 * 1024)
                is_large_image = img.size[0] * img.size[1] > 4000000

                if img.size[0] > max_size[0] or img.size[1] > max_size[1] or file_size_mb > max_file_size_mb:
                    ratio = min(max_size[0] / img.size[0], max_size[1] / img.size[1])
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    # Web/批处理优先速度：大图用 NEAREST，其它用 BILINEAR（比 LANCZOS 快很多）
                    resample_method = Image.Resampling.NEAREST if is_large_image else Image.Resampling.BILINEAR
                    img = img.resize(new_size, resample_method)
                    if verbose:
                        console.detail(f"  图片尺寸: {original_size} -> {new_size}, 文件大小: {file_size_mb:.2f}MB")

                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                buffer = io.BytesIO()
                quality = 85 if not is_large_image else 75
                # optimize=True 会显著增加 CPU 时间，批处理场景优先速度
                img.save(buffer, format="JPEG", quality=quality, optimize=False)

                while buffer.tell() / (1024 * 1024) > max_file_size_mb and quality > 30:
                    quality -= 10 if is_large_image else 5
                    buffer.seek(0)
                    buffer.truncate(0)
                    img.save(buffer, format="JPEG", quality=quality, optimize=False)

                buffer.seek(0)
                result = buffer.read(), "image/jpeg"
                del img
                del buffer
                return result
        except (IOError, OSError) as e:
            raise ValueError(f"图片压缩失败: {e}")
        finally:
            # 仅在超大图时做一次 GC，避免每张图都 gc.collect() 导致“慢一半”
            if is_large_image:
                gc.collect()


def get_image_mime_type(image_path: Path) -> str:
    """获取图片文件的MIME类型"""
    ext = image_path.suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    return mime_types.get(ext, "image/jpeg")


def encode_image_to_base64(image_path: Path, mime_type: str) -> str:
    """将图片文件编码为base64格式"""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{image_data}"


def get_image_url(image_path: Path, max_image_size=(1024, 1024), max_file_size_mb=1,
                  enable_compression=True, verbose=True) -> str:
    """获取图片的base64 URL，支持缓存和压缩"""
    if not image_path.exists() or not image_path.is_file():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    cached_url = _IMAGE_CACHE.get(image_path, max_image_size, max_file_size_mb, enable_compression)
    if cached_url is not None:
        return cached_url

    if not enable_compression:
        mime_type = get_image_mime_type(image_path)
        result_url = encode_image_to_base64(image_path, mime_type)
    else:
        if not HAS_PIL:
            if verbose:
                console.blank()
                console.error("  ❌ Pillow 未安装，无法压缩图片！")
                console.info("  请运行: pip install Pillow")
            raise ImportError("需要安装Pillow才能处理大于0.5MB的图片: pip install Pillow")

        try:
            with Image.open(image_path) as img:
                file_size_mb = image_path.stat().st_size / (1024 * 1024)
                needs_compression = (
                    img.size[0] > max_image_size[0]
                    or img.size[1] > max_image_size[1]
                    or file_size_mb > 0.5
                )

            if needs_compression:
                image_data_bytes, mime_type = compress_image(
                    image_path, max_image_size, max_file_size_mb, verbose=verbose
                )
                image_data = base64.b64encode(image_data_bytes).decode("utf-8")
                result_url = f"data:{mime_type};base64,{image_data}"
            else:
                mime_type = get_image_mime_type(image_path)
                result_url = encode_image_to_base64(image_path, mime_type)
        except (IOError, OSError, ValueError) as e:
            if verbose:
                console.error(f"  ❌ 错误: {e}")
            raise

    _IMAGE_CACHE.put(image_path, max_image_size, max_file_size_mb, enable_compression, result_url)
    return result_url


def get_image_files(input_dir: str | Path, project_root: Path) -> List[Path]:
    """获取目录下所有图片文件"""
    input_path = Path(input_dir)
    if not input_path.exists():
        if not input_path.is_absolute():
            input_path = project_root / input_dir
        if not input_path.exists():
            console.blank()
            console.error(f"错误: 输入文件夹不存在: {input_path}")
            raise FileNotFoundError(f"输入文件夹不存在: {input_path}")

    if not input_path.is_dir():
        raise ValueError(f"路径不是文件夹: {input_dir}")

    image_files = set()
    for ext in IMAGE_EXTENSIONS:
        for file in input_path.glob(f"*{ext}"):
            image_files.add(file)
        for file in input_path.glob(f"*{ext.upper()}"):
            image_files.add(file)

    if not image_files:
        raise FileNotFoundError(
            f"在文件夹 {input_path} 中未找到支持的图片文件。支持的格式: {', '.join(sorted(IMAGE_EXTENSIONS))}")

    return sorted(list(image_files))
