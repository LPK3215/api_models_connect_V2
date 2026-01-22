"""
依赖检测器
检测必需和可选的 Python 包
"""

import importlib
from typing import Dict, Tuple, Optional

from .base import BaseChecker, CheckResult


class DepsChecker(BaseChecker):
    """依赖检测器"""

    name = "依赖检测"
    description = "检测必需和可选的 Python 包"

    # 核心依赖（必须安装）
    CORE_DEPS = {
        "yaml": ("pyyaml", "配置文件解析"),
        "requests": ("requests", "HTTP 请求"),
        "PIL": ("Pillow", "图片处理"),
    }

    # 云API依赖
    CLOUD_API_DEPS = {
        "openai": ("openai", "OpenAI 兼容 API 调用"),
    }

    # 可选依赖
    OPTIONAL_DEPS = {
        "colorama": ("colorama", "彩色终端输出"),
        "gradio": ("gradio", "Web 界面"),
    }

    def check(self) -> CheckResult:
        """执行依赖检测"""
        sub_results = []

        # 检测核心依赖
        core_result = self._check_deps_group("核心依赖", self.CORE_DEPS, required=True)
        sub_results.append(core_result)

        # 检测云API依赖
        cloud_result = self._check_deps_group("云API依赖", self.CLOUD_API_DEPS, required=True)
        sub_results.append(cloud_result)

        # 检测可选依赖
        optional_result = self._check_deps_group("可选依赖", self.OPTIONAL_DEPS, required=False)
        sub_results.append(optional_result)

        # 汇总结果
        required_results = [r for r in sub_results if "可选" not in r.message]
        all_required_passed = all(r.success for r in required_results)

        return CheckResult(
            success=all_required_passed,
            message="依赖检测完成" if all_required_passed else "缺少必需依赖",
            sub_results=sub_results,
            fix_key=None if all_required_passed else "deps_missing"
        )

    def _check_deps_group(self, group_name: str, deps: Dict[str, Tuple[str, str]], required: bool) -> CheckResult:
        """检测一组依赖"""
        results = []
        missing = []

        for module_name, (package_name, description) in deps.items():
            installed, version = self._check_package(module_name)

            if installed:
                version_str = f" (v{version})" if version else ""
                results.append(CheckResult(
                    success=True,
                    message=f"{package_name}{version_str}: 已安装"
                ))
            else:
                missing.append(package_name)
                results.append(CheckResult(
                    success=False,
                    message=f"{package_name}: 未安装 - {description}",
                    fix_key=f"install_{package_name.lower()}"
                ))

        all_installed = len(missing) == 0

        if required:
            status = "✓" if all_installed else f"缺少 {len(missing)} 个"
        else:
            status = "✓" if all_installed else f"{len(missing)} 个未安装（可选）"

        return CheckResult(
            success=all_installed or not required,
            message=f"{group_name}: {status}",
            details={"missing": missing} if missing else {},
            sub_results=results,
            fix_key=f"deps_{group_name.lower()}" if missing and required else None
        )

    def _check_package(self, module_name: str) -> Tuple[bool, Optional[str]]:
        """检测单个包是否安装"""
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", None)
            return True, version
        except ImportError:
            return False, None
