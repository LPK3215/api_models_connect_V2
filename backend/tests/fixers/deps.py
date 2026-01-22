"""
依赖修复器
生成依赖安装命令
"""

from typing import Optional

from .base import BaseFixer, FixSuggestion


class DepsFixer(BaseFixer):
    """依赖修复器"""

    # 包安装命令
    INSTALL_COMMANDS = {
        "pyyaml": "pip install pyyaml",
        "requests": "pip install requests",
        "pillow": "pip install Pillow",
        "openai": "pip install openai",
        "colorama": "pip install colorama",
        "gradio": "pip install gradio",
    }

    def get_fix(self, fix_key: str, **context) -> Optional[FixSuggestion]:
        """根据 fix_key 获取修复建议"""

        if fix_key == "deps_missing":
            return self._fix_deps_missing(context.get("missing", []))

        if fix_key.startswith("install_"):
            package = fix_key.replace("install_", "")
            return self._fix_single_package(package)

        if fix_key == "deps_核心依赖":
            return self._fix_core_deps()

        if fix_key == "deps_云api依赖":
            return self._fix_cloud_api_deps()

        return None

    def _fix_deps_missing(self, missing: list) -> FixSuggestion:
        """修复缺失的依赖"""
        commands = []
        for pkg in missing:
            pkg_lower = pkg.lower()
            if pkg_lower in self.INSTALL_COMMANDS:
                cmd = self.INSTALL_COMMANDS[pkg_lower]
                commands.append(cmd)

        if not commands:
            commands = [f"pip install {' '.join(missing)}"]

        return FixSuggestion(
            title="安装缺失的依赖",
            description=f"缺少以下依赖包: {', '.join(missing)}",
            commands=commands
        )

    def _fix_single_package(self, package: str) -> FixSuggestion:
        """修复单个包"""
        pkg_lower = package.lower()

        if pkg_lower in self.INSTALL_COMMANDS:
            cmd = self.INSTALL_COMMANDS[pkg_lower]
            return FixSuggestion(
                title=f"安装 {package}",
                description=f"需要安装 {package}",
                commands=[cmd]
            )

        return FixSuggestion(
            title=f"安装 {package}",
            description=f"需要安装 {package}",
            commands=[f"pip install {package}"]
        )

    def _fix_core_deps(self) -> FixSuggestion:
        """修复核心依赖"""
        return FixSuggestion(
            title="安装核心依赖",
            description="缺少项目运行必需的核心依赖",
            commands=[
                "pip install pyyaml requests Pillow"
            ]
        )

    def _fix_cloud_api_deps(self) -> FixSuggestion:
        """修复云API依赖"""
        return FixSuggestion(
            title="安装云API依赖",
            description="缺少调用云API所需的依赖",
            commands=[
                "pip install openai"
            ]
        )
