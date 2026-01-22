"""
检测器模块
- 底层检测器: EnvChecker 等（执行实际检测）
- 高层封装: CloudEnvironmentChecker, LocalEnvironmentChecker（提供交互界面）
"""

from .api import APIChecker
from .base import CheckResult, BaseChecker
from .cloud_checker import CloudEnvironmentChecker
from .deps import DepsChecker
from .env import EnvChecker
from .local_checker import LocalEnvironmentChecker
from .local_ui import LocalUI
from .paths import PathChecker

__all__ = [
    # 底层检测器
    "CheckResult",
    "BaseChecker",
    "EnvChecker",
    "DepsChecker",
    "APIChecker",
    "PathChecker",
    # 高层封装
    "CloudEnvironmentChecker",
    "LocalEnvironmentChecker",
    "LocalUI",
]
