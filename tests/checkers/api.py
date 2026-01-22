"""
API 检测器
检测 API 密钥配置和连通性
"""

import os
from typing import Dict, List

from .base import BaseChecker, CheckResult


class APIChecker(BaseChecker):
    """API 检测器"""

    name = "API 检测"
    description = "检测 API 密钥配置和连通性"

    # API 密钥配置
    API_KEYS = {
        "DASHSCOPE_API_KEY": {
            "name": "阿里云 DashScope",
            "test_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/models",
            "provider": "aliyun"
        },
        "ARK_API_KEY": {
            "name": "豆包/火山方舟",
            "test_url": "https://ark.cn-beijing.volces.com/api/v3/models",
            "provider": "doubao"
        },
        "MODELSCOPE_ACCESS_TOKEN": {
            "name": "魔塔 ModelScope",
            "test_url": "https://api-inference.modelscope.cn/v1/models",
            "provider": "modelscope"
        },
        "HUNYUAN_API_KEY": {
            "name": "腾讯混元",
            "test_url": "https://api.hunyuan.cloud.tencent.com/v1/models",
            "provider": "tencent"
        },
    }

    def __init__(self, test_connectivity: bool = True):
        """
        Args:
            test_connectivity: 是否测试 API 连通性
        """
        self.test_connectivity = test_connectivity

    def check(self) -> CheckResult:
        """执行 API 检测"""
        sub_results = []
        configured_count = 0

        for env_key, info in self.API_KEYS.items():
            result = self._check_api_key(env_key, info)
            sub_results.append(result)
            if result.success:
                configured_count += 1

        # 至少需要配置一个 API
        has_any_api = configured_count > 0

        return CheckResult(
            success=has_any_api,
            message=f"API 密钥: {configured_count}/{len(self.API_KEYS)} 已配置",
            details={
                "configured": configured_count,
                "total": len(self.API_KEYS),
            },
            sub_results=sub_results,
            fix_key=None if has_any_api else "no_api_key"
        )

    def _check_api_key(self, env_key: str, info: Dict) -> CheckResult:
        """检测单个 API 密钥"""
        api_key = os.environ.get(env_key)
        name = info["name"]

        if not api_key:
            return CheckResult(
                success=False,
                message=f"{name}: 未配置",
                details={"env_key": env_key},
                fix_key=f"api_key_{info['provider']}"
            )

        # 密钥已配置
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"

        # 测试连通性
        if self.test_connectivity:
            connectivity = self._test_connectivity(api_key, info)
            if connectivity:
                return CheckResult(
                    success=True,
                    message=f"{name}: 已配置且连通 ✓",
                    details={"env_key": env_key, "masked_key": masked_key}
                )
            else:
                return CheckResult(
                    success=True,  # 密钥配置了就算成功
                    message=f"{name}: 已配置 (连通性未验证)",
                    details={"env_key": env_key, "masked_key": masked_key, "warning": "无法验证连通性"}
                )

        return CheckResult(
            success=True,
            message=f"{name}: 已配置 ({masked_key})",
            details={"env_key": env_key, "masked_key": masked_key}
        )

    def _test_connectivity(self, api_key: str, info: Dict) -> bool:
        """测试 API 连通性"""
        try:
            import requests

            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(info["test_url"], headers=headers, timeout=5)

            # 200, 401, 403 都说明能连通（401/403 是认证问题，但网络是通的）
            return response.status_code in [200, 401, 403]
        except Exception:
            return False

    def get_configured_providers(self) -> List[str]:
        """获取已配置的云平台列表"""
        configured = []
        for env_key, info in self.API_KEYS.items():
            if os.environ.get(env_key):
                configured.append(info["provider"])
        return configured
