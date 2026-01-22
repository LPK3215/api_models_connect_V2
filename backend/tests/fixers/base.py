"""
修复器基类
定义统一的修复建议格式
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FixSuggestion:
    """修复建议"""
    title: str  # 建议标题
    description: str  # 问题描述
    commands: List[str] = field(default_factory=list)  # 修复命令（可直接复制执行）
    manual_steps: List[str] = field(default_factory=list)  # 手动操作步骤
    docs_url: Optional[str] = None  # 相关文档链接

    def print_suggestion(self) -> None:
        """打印修复建议"""
        print()
        print(f"     🔧 {self.title}")
        print(f"        问题: {self.description}")

        if self.commands:
            print()
            print("        📋 执行以下命令修复:")
            for cmd in self.commands:
                print(f"           {cmd}")

        if self.manual_steps:
            print()
            print("        📝 手动操作步骤:")
            for i, step in enumerate(self.manual_steps, 1):
                print(f"           {i}. {step}")

        if self.docs_url:
            print()
            print(f"        📚 参考文档: {self.docs_url}")


class BaseFixer(ABC):
    """修复器基类"""

    @abstractmethod
    def get_fix(self, fix_key: str, **context) -> Optional[FixSuggestion]:
        """根据 fix_key 获取修复建议"""
        pass
