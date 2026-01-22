"""
路径检测器
检测项目路径和配置文件路径
"""

from pathlib import Path

from .base import BaseChecker, CheckResult


class PathChecker(BaseChecker):
    """路径检测器"""

    name = "路径检测"
    description = "检测项目路径和配置文件"

    # 必需的配置文件
    REQUIRED_CONFIG_FILES = [
        "config/models.yml",
        "config/prompts/default.yml",
    ]

    # 必需的目录
    REQUIRED_DIRS = [
        "data/inputs",
        "data/outputs",
    ]

    def check(self) -> CheckResult:
        """执行路径检测"""
        sub_results = []

        # 检测配置文件
        config_result = self._check_config_files()
        sub_results.append(config_result)

        # 检测数据目录
        dir_result = self._check_directories()
        sub_results.append(dir_result)

        # 汇总
        all_passed = all(r.success for r in sub_results)

        return CheckResult(
            success=all_passed,
            message="路径检测完成" if all_passed else "路径检测发现问题",
            sub_results=sub_results
        )

    def _check_config_files(self) -> CheckResult:
        """检测配置文件"""
        project_root = Path(__file__).parent.parent.parent
        
        missing_files = []
        for file_path in self.REQUIRED_CONFIG_FILES:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            return CheckResult(
                success=False,
                message=f"缺少配置文件: {', '.join(missing_files)}",
                details={"missing_files": missing_files},
                fix_key="config_files_missing"
            )

        return CheckResult(
            success=True,
            message="配置文件完整",
            details={"files": self.REQUIRED_CONFIG_FILES}
        )

    def _check_directories(self) -> CheckResult:
        """检测必需目录"""
        project_root = Path(__file__).parent.parent.parent
        
        missing_dirs = []
        for dir_path in self.REQUIRED_DIRS:
            full_path = project_root / dir_path
            if not full_path.exists():
                # 尝试创建目录
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                except Exception:
                    missing_dirs.append(dir_path)

        if missing_dirs:
            return CheckResult(
                success=False,
                message=f"缺少目录: {', '.join(missing_dirs)}",
                details={"missing_dirs": missing_dirs},
                fix_key="dirs_missing"
            )

        return CheckResult(
            success=True,
            message="目录结构完整",
            details={"dirs": self.REQUIRED_DIRS}
        )
