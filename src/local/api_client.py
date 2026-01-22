"""
API客户端模块
包含API客户端池、速率限制器等功能
"""
from __future__ import annotations

import threading
import time
from typing import Dict


class APIClientPool:
    """API客户端池，复用OpenAI客户端实例以提高性能"""

    def __init__(self):
        self._clients = {}

    def get_client(self, api_key: str, base_url: str, timeout: float):
        """获取或创建客户端实例"""
        key = f"{api_key[:10] if api_key else 'none'}_{base_url}_{timeout}"

        if key not in self._clients:
            from openai import OpenAI
            self._clients[key] = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout
            )

        return self._clients[key]

    def clear(self):
        """清空客户端池"""
        self._clients.clear()


class RequestRateLimiter:
    """请求速率限制器"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_request_at: Dict[str, float] = {}

    def wait(self, key: str, min_interval_s: float) -> None:
        """等待直到可以发送下一个请求"""
        if not min_interval_s or min_interval_s <= 0:
            return
        now = time.monotonic()
        with self._lock:
            last = self._last_request_at.get(key, 0.0)
            earliest = last + float(min_interval_s)
            sleep_s = max(0.0, earliest - now)
            self._last_request_at[key] = now + sleep_s
        if sleep_s:
            time.sleep(sleep_s)


# 全局实例
_RATE_LIMITER = RequestRateLimiter()
_CLIENT_POOL = APIClientPool()


def get_rate_limiter() -> RequestRateLimiter:
    """获取全局速率限制器"""
    return _RATE_LIMITER


def get_client_pool() -> APIClientPool:
    """获取全局客户端池"""
    return _CLIENT_POOL
