"""
修复建议模块
根据检测结果的 fix_key 生成修复命令
"""

from .base import BaseFixer, FixSuggestion
from .config import ConfigFixer
from .deps import DepsFixer
from .env import EnvFixer

__all__ = [
    "BaseFixer",
    "FixSuggestion",
    "DepsFixer",
    "ConfigFixer",
    "EnvFixer",
]
