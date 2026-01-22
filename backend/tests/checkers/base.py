"""
检测器基类
定义统一的检测结果格式和接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class CheckResult:
    """检测结果"""
    success: bool  # 是否通过
    message: str  # 结果描述
    details: Dict[str, Any] = field(default_factory=dict)  # 详细信息
    fix_key: Optional[str] = None  # 修复建议的key
    sub_results: List["CheckResult"] = field(default_factory=list)  # 子检测结果

    def __str__(self) -> str:
        icon = "✅" if self.success else "❌"
        return f"{icon} {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "details": self.details,
            "fix_key": self.fix_key,
            "sub_results": [r.to_dict() for r in self.sub_results]
        }


class BaseChecker(ABC):
    """检测器基类"""

    name: str = "基础检测器"
    description: str = "检测器描述"

    @abstractmethod
    def check(self) -> CheckResult:
        """执行检测，返回检测结果"""
        pass

    def print_result(self, result: CheckResult, indent: int = 0) -> None:
        """打印检测结果"""
        prefix = "     " + "  " * indent
        icon = "✅" if result.success else "❌"
        print(f"{prefix}{icon} {result.message}")

        # 打印详细信息（只显示重要的）
        if result.details and indent == 0:
            for key, value in result.details.items():
                if key not in ["warning", "tip"]:  # 跳过提示类信息
                    print(f"{prefix}   └─ {key}: {value}")

        # 打印子结果
        for sub in result.sub_results:
            self.print_result(sub, indent + 1)
