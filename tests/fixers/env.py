"""
环境修复器
生成环境配置修复建议
"""

import platform
from typing import Optional

from .base import BaseFixer, FixSuggestion


class EnvFixer(BaseFixer):
    """环境修复器"""

    def get_fix(self, fix_key: str, **context) -> Optional[FixSuggestion]:
        """根据 fix_key 获取修复建议"""

        if fix_key == "python_version_low":
            return self._fix_python_version()

        if fix_key == "no_api_key":
            return self._fix_no_api_key()

        if fix_key.startswith("api_key_"):
            provider = fix_key.replace("api_key_", "")
            return self._fix_api_key(provider)

        return None

    def _fix_python_version(self) -> FixSuggestion:
        """修复 Python 版本"""
        return FixSuggestion(
            title="升级 Python 版本",
            description="当前 Python 版本过低，需要 >= 3.9",
            manual_steps=[
                "下载 Python 3.10+ 从 https://www.python.org/downloads/",
                "安装后重新创建虚拟环境",
                "重新安装项目依赖",
            ],
            docs_url="https://www.python.org/downloads/"
        )

    def _fix_no_api_key(self) -> FixSuggestion:
        """修复无 API 密钥"""
        is_windows = platform.system() == "Windows"

        if is_windows:
            commands = [
                "# Windows CMD:",
                "set DASHSCOPE_API_KEY=your_api_key_here",
                "",
                "# Windows PowerShell:",
                "$env:DASHSCOPE_API_KEY='your_api_key_here'",
            ]
        else:
            commands = [
                "# Linux/macOS:",
                "export DASHSCOPE_API_KEY='your_api_key_here'",
                "",
                "# 永久生效（添加到 ~/.bashrc）:",
                "echo \"export DASHSCOPE_API_KEY='your_api_key_here'\" >> ~/.bashrc",
                "source ~/.bashrc",
            ]

        return FixSuggestion(
            title="配置 API 密钥",
            description="未配置任何云平台 API 密钥",
            commands=commands,
            manual_steps=[
                "选择一个云平台注册账号",
                "获取 API 密钥",
                "设置对应的环境变量",
            ]
        )

    def _fix_api_key(self, provider: str) -> FixSuggestion:
        """修复特定平台的 API 密钥"""
        provider_info = {
            "aliyun": {
                "name": "阿里云 DashScope",
                "env_key": "DASHSCOPE_API_KEY",
                "url": "https://dashscope.console.aliyun.com/apiKey",
            },
            "doubao": {
                "name": "豆包/火山方舟",
                "env_key": "ARK_API_KEY",
                "url": "https://console.volcengine.com/ark",
            },
            "modelscope": {
                "name": "魔塔 ModelScope",
                "env_key": "MODELSCOPE_ACCESS_TOKEN",
                "url": "https://modelscope.cn/my/myaccesstoken",
            },
            "tencent": {
                "name": "腾讯混元",
                "env_key": "HUNYUAN_API_KEY",
                "url": "https://console.cloud.tencent.com/hunyuan",
            },
        }

        info = provider_info.get(provider, {
            "name": provider,
            "env_key": f"{provider.upper()}_API_KEY",
            "url": None,
        })

        is_windows = platform.system() == "Windows"

        if is_windows:
            cmd = f"set {info['env_key']}=your_api_key_here"
        else:
            cmd = f"export {info['env_key']}='your_api_key_here'"

        return FixSuggestion(
            title=f"配置 {info['name']} API 密钥",
            description=f"未配置 {info['name']} 的 API 密钥",
            commands=[cmd],
            manual_steps=[
                f"访问 {info['url']} 获取 API 密钥" if info['url'] else "获取 API 密钥",
                f"设置环境变量 {info['env_key']}",
            ],
            docs_url=info['url']
        )
