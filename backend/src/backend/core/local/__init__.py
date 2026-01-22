"""
本地开发机模块
在本地电脑上运行，调用云平台API
"""
from backend.core.local.api_client import (
    get_client_pool, get_rate_limiter,
)
from backend.core.local.cloud_processor import process_images_with_cloud_api
from backend.core.local.image_utils import (
    get_image_url, get_image_files, compress_image, IMAGE_EXTENSIONS,
)
from backend.core.local.result_handler import (
    extract_text_from_message, parse_json_from_model_output,
    get_output_file_path, get_latest_output_file_path, save_result,
)

__all__ = [
    "get_image_url", "get_image_files", "compress_image", "IMAGE_EXTENSIONS",
    "get_client_pool", "get_rate_limiter",
    "extract_text_from_message", "parse_json_from_model_output",
    "get_output_file_path", "get_latest_output_file_path", "save_result",
    "process_images_with_cloud_api",
]
