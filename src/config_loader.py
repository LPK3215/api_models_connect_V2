"""
多云模型配置加载器

- 从 config/models.yml 读取各云厂商与模型的配置信息
- 构建 PROVIDERS 结构，供 CLI 与处理管线查询使用
- 暴露函数：
  - load_model_config(): 返回完整的 YAML 配置字典
  - get_provider(provider_key): 获取指定厂商的 info 和 model_pool
  - get_model(provider_key, model_key): 合并厂商 defaults 后的模型配置
- 主要被以下模块依赖：
  - src.cli: 用 PROVIDERS 构建交互式模型列表
  - src.processor: 通过 get_provider / get_model 获取 api_base_url、env_key 等
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


class _ConfigManager:
    """配置管理器，支持基于文件修改时间的智能缓存"""

    def __init__(self):
        self._cache: Dict[str, Any] | None = None
        self._last_mtime: float = 0
        self._config_path: Path | None = None

    def load_model_config(self) -> Dict[str, Any]:
        """加载模型配置，支持文件修改检测"""
        if self._config_path is None:
            project_root = Path(__file__).resolve().parent.parent
            self._config_path = project_root / "config" / "models.yml"

        # 检查文件是否存在
        if not self._config_path.exists():
            return {}

        # 获取文件修改时间
        current_mtime = self._config_path.stat().st_mtime

        # 如果缓存为空或文件已修改，重新加载
        if self._cache is None or current_mtime > self._last_mtime:
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    self._cache = yaml.safe_load(f) or {}
                self._last_mtime = current_mtime
            except Exception:
                # 如果读取失败，返回空配置而不是崩溃
                if self._cache is None:
                    self._cache = {}

        return self._cache

    def clear_cache(self):
        """清空缓存，强制重新加载"""
        self._cache = None
        self._last_mtime = 0


# 全局配置管理器实例
_config_manager = _ConfigManager()


def load_model_config() -> Dict[str, Any]:
    """加载模型配置（带缓存优化）"""
    return _config_manager.load_model_config()


def _build_providers() -> Dict[str, Dict[str, Any]]:
    """构建云平台配置，使用缓存优化"""
    cfg = _config_manager.load_model_config()  # 使用缓存管理器
    providers_cfg = cfg.get("providers", {}) or {}
    providers: Dict[str, Dict[str, Any]] = {}
    for key, provider in providers_cfg.items():
        models = provider.get("models", {}) or {}
        providers[key] = {
            "info": {k: v for k, v in provider.items() if k != "models"},
            "model_pool": models,
        }
    return providers


# 延迟初始化PROVIDERS，避免模块导入时的重复构建
_providers_cache: Dict[str, Dict[str, Any]] | None = None


def get_providers() -> Dict[str, Dict[str, Any]]:
    """获取云平台配置（带缓存）"""
    global _providers_cache
    if _providers_cache is None:
        _providers_cache = _build_providers()
    return _providers_cache


def refresh_providers():
    """刷新云平台配置缓存"""
    global _providers_cache
    _config_manager.clear_cache()
    _providers_cache = None


# 为了保持向后兼容，保留PROVIDERS变量
PROVIDERS: Dict[str, Dict[str, Any]] = {}


def get_provider(provider_key: str) -> Dict[str, Any]:
    providers = get_providers()  # 使用缓存版本
    if provider_key not in providers:
        available = ", ".join(providers.keys())
        raise KeyError(f"厂商 '{provider_key}' 不存在。可用厂商: {available}")
    return providers[provider_key]


def get_model(provider_key: str, model_key: str) -> Dict[str, Any]:
    provider = get_provider(provider_key)
    model_pool = provider["model_pool"]
    if model_key not in model_pool:
        available_keys = ", ".join(model_pool.keys())
        raise KeyError(f"模型键 '{model_key}' 不存在。可用模型: {available_keys}")

    merged = dict(provider["info"].get("defaults", {}))
    merged.update(model_pool[model_key])
    return merged
