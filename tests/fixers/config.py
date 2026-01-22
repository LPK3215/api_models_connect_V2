"""
配置修复器
生成配置文件修复建议
"""

import platform
from typing import Optional

from .base import BaseFixer, FixSuggestion


class ConfigFixer(BaseFixer):
    """配置修复器"""

    def get_fix(self, fix_key: str, **context) -> Optional[FixSuggestion]:
        """根据 fix_key 获取修复建议"""

        if fix_key == "project_structure_incomplete":
            return self._fix_project_structure(context)

        if fix_key == "config_file_missing":
            return self._fix_config_file()

        return None

    def _fix_project_structure(self, context: dict) -> FixSuggestion:
        """修复项目结构"""
        missing_dirs = context.get("missing_dirs", [])
        missing_files = context.get("missing_files", [])

        commands = []

        # 创建缺失目录
        if missing_dirs:
            if platform.system() == "Windows":
                for d in missing_dirs:
                    # Python 3.10 不支持 f-string 中包含反斜杠，需要先处理
                    win_path = d.replace('/', '\\')
                    commands.append(f"mkdir {win_path}")
            else:
                commands.append(f"mkdir -p {' '.join(missing_dirs)}")

        manual_steps = []
        if missing_files:
            manual_steps.append(f"缺失的配置文件: {', '.join(missing_files)}")
            manual_steps.append("请从项目模板或备份中恢复这些文件")

        return FixSuggestion(
            title="修复项目结构",
            description="项目目录结构不完整",
            commands=commands if commands else None,
            manual_steps=manual_steps if manual_steps else None
        )

    def _fix_config_file(self) -> FixSuggestion:
        """修复配置文件"""
        return FixSuggestion(
            title="修复配置文件",
            description="配置文件缺失或损坏",
            manual_steps=[
                "检查 config/models.yml 是否存在",
                "如果不存在，从项目模板复制",
                "确保 YAML 格式正确",
            ]
        )
