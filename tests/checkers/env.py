"""
环境检测器
检测 Python 版本、操作系统等基础环境
"""

import platform
import sys
from pathlib import Path

from .base import BaseChecker, CheckResult


class EnvChecker(BaseChecker):
    """环境检测器"""

    name = "环境检测"
    description = "检测 Python 版本、操作系统等基础环境"

    # Python 版本要求
    MIN_PYTHON_VERSION = (3, 9)
    RECOMMENDED_PYTHON_VERSION = (3, 10)

    def check(self) -> CheckResult:
        """执行环境检测"""
        sub_results = []

        # 检测 Python 版本
        sub_results.append(self._check_python_version())

        # 检测操作系统
        sub_results.append(self._check_os())

        # 检测项目结构
        sub_results.append(self._check_project_structure())

        # 汇总结果
        all_passed = all(r.success for r in sub_results)
        critical_passed = sub_results[0].success  # Python 版本是关键

        return CheckResult(
            success=critical_passed,
            message="环境检测完成" if all_passed else "环境检测发现问题",
            details={
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": platform.system(),
            },
            sub_results=sub_results
        )

    def _check_python_version(self) -> CheckResult:
        """检测 Python 版本"""
        current = (sys.version_info.major, sys.version_info.minor)
        version_str = f"{current[0]}.{current[1]}"

        if current < self.MIN_PYTHON_VERSION:
            return CheckResult(
                success=False,
                message=f"Python 版本过低: {version_str} (需要 >= {self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]})",
                fix_key="python_version_low"
            )
        elif current < self.RECOMMENDED_PYTHON_VERSION:
            return CheckResult(
                success=True,
                message=f"Python 版本: {version_str} (建议升级到 {self.RECOMMENDED_PYTHON_VERSION[0]}.{self.RECOMMENDED_PYTHON_VERSION[1]}+)",
                details={"warning": "版本较低，部分功能可能受限"}
            )
        else:
            return CheckResult(
                success=True,
                message=f"Python 版本: {version_str} ✓"
            )

    def _check_os(self) -> CheckResult:
        """检测操作系统"""
        os_name = platform.system()
        os_info = {
            "system": os_name,
            "release": platform.release(),
            "machine": platform.machine(),
        }

        if os_name == "Windows":
            env_type = "本地开发环境 (Windows)"
        elif os_name == "Linux":
            # 检测是否为云服务器
            if Path("/root/autodl-tmp").exists():
                env_type = "云服务器 (AutoDL)"
            else:
                env_type = "Linux 服务器"
        elif os_name == "Darwin":
            env_type = "本地开发环境 (macOS)"
        else:
            env_type = f"其他系统 ({os_name})"

        return CheckResult(
            success=True,
            message=f"操作系统: {env_type}",
            details=os_info
        )

    def _check_project_structure(self) -> CheckResult:
        """检测项目结构"""
        project_root = Path(__file__).parent.parent.parent

        required_dirs = ["src", "config", "data/inputs", "data/outputs"]
        required_files = ["config/models.yml", "src/processor.py", "src/config.py"]

        missing_dirs = []
        missing_files = []

        for d in required_dirs:
            if not (project_root / d).exists():
                missing_dirs.append(d)

        for f in required_files:
            if not (project_root / f).exists():
                missing_files.append(f)

        if missing_dirs or missing_files:
            return CheckResult(
                success=False,
                message="项目结构不完整",
                details={
                    "missing_dirs": missing_dirs,
                    "missing_files": missing_files,
                },
                fix_key="project_structure_incomplete"
            )

        return CheckResult(
            success=True,
            message="项目结构完整 ✓"
        )
