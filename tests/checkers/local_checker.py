"""
本地环境检测核心模块
将检测逻辑从 check_local.py 中分离出来
"""

import sys
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class LocalEnvironmentChecker:
    """本地环境检测器"""

    def __init__(self):
        self.project_root = project_root

    def run_full_check(self) -> Dict[str, Any]:
        """运行完整环境检测"""
        from tests.checkers import EnvChecker, DepsChecker, APIChecker
        from tests.fixers import DepsFixer, EnvFixer

        results = {
            'all_passed': True,
            'fix_suggestions': [],
            'checks': {}
        }

        # 1. 环境检测
        env_checker = EnvChecker()
        env_result = env_checker.check()
        results['checks']['env'] = env_result
        if not env_result.success:
            results['all_passed'] = False

        # 2. 依赖检测
        deps_checker = DepsChecker()
        deps_result = deps_checker.check()
        results['checks']['deps'] = deps_result
        if not deps_result.success:
            results['all_passed'] = False
            deps_fixer = DepsFixer()
            if deps_result.fix_key:
                fix = deps_fixer.get_fix(deps_result.fix_key)
                if fix:
                    results['fix_suggestions'].append(fix)

        # 3. API密钥检测
        api_checker = APIChecker(test_connectivity=False)
        api_result = api_checker.check()
        results['checks']['api'] = api_result
        if not api_result.success:
            results['all_passed'] = False
            env_fixer = EnvFixer()
            fix = env_fixer.get_fix("no_api_key")
            if fix:
                results['fix_suggestions'].append(fix)

        return results

    def run_api_key_check(self) -> Dict[str, Any]:
        """运行API密钥检测"""
        from tests.checkers import APIChecker
        from tests.fixers import EnvFixer

        checker = APIChecker(test_connectivity=False)
        result = checker.check()

        # 获取未配置的API修复建议
        unconfigured = [sub for sub in result.sub_results if not sub.success]
        fix_suggestions = []

        if unconfigured:
            env_fixer = EnvFixer()
            for sub in unconfigured[:2]:  # 只显示前2个
                if sub.fix_key:
                    fix = env_fixer.get_fix(sub.fix_key)
                    if fix:
                        fix_suggestions.append(fix)

        return {
            'result': result,
            'fix_suggestions': fix_suggestions
        }

    def run_connectivity_test(self) -> Dict[str, Any]:
        """运行API连通性测试"""
        from tests.checkers import APIChecker

        checker = APIChecker(test_connectivity=True)
        result = checker.check()

        return {'result': result}

    def run_function_test(self) -> Dict[str, Any]:
        """运行功能测试"""
        from tests.checkers import APIChecker

        # 检查测试图片
        test_images_dir = self.project_root / "data" / "inputs"
        images = []
        if test_images_dir.exists():
            images = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))

        # 检查API配置
        api_checker = APIChecker(test_connectivity=False)
        configured = api_checker.get_configured_providers()

        return {
            'test_images_dir': test_images_dir,
            'images_count': len(images),
            'first_image': images[0].name if images else None,
            'configured_providers': configured,
            'dir_exists': test_images_dir.exists()
        }

    def show_available_models(self) -> Dict[str, Any]:
        """显示可用模型"""
        try:
            from src.config_loader import get_providers
            providers = get_providers()

            models_info = {}
            for provider_key, provider_data in providers.items():
                # 跳过本地模型
                if provider_key in ["local", "local_api"]:
                    continue

                info = provider_data.get("info", {})
                models = provider_data.get("model_pool", {})

                models_info[provider_key] = {
                    'display_name': info.get('display_name', provider_key),
                    'env_key': info.get('defaults', {}).get('env_key', 'N/A'),
                    'models': models
                }

            return {'success': True, 'models_info': models_info}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def run_diagnosis(self) -> Dict[str, Any]:
        """运行问题诊断"""
        from tests.checkers import EnvChecker, DepsChecker, APIChecker
        from tests.fixers import DepsFixer, EnvFixer, ConfigFixer

        issues = []

        # 检测各项
        checkers = [
            ("环境问题", EnvChecker()),
            ("依赖问题", DepsChecker()),
            ("API配置问题", APIChecker(test_connectivity=False))
        ]

        for issue_name, checker in checkers:
            result = checker.check()
            if not result.success:
                issues.append((issue_name, result))

        # 生成修复建议
        fixers = [DepsFixer(), EnvFixer(), ConfigFixer()]
        fix_suggestions = []

        for issue_name, result in issues:
            for sub in result.sub_results:
                if not sub.success and sub.fix_key:
                    for fixer in fixers:
                        fix = fixer.get_fix(sub.fix_key)
                        if fix:
                            fix_suggestions.append((issue_name, fix))
                            break

        return {
            'issues': issues,
            'fix_suggestions': fix_suggestions,
            'has_issues': len(issues) > 0
        }

    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检测项目"""
        from tests.checkers import EnvChecker, DepsChecker

        results = []

        print()
        print("  " + "=" * 70)
        print("  🔥 本地环境全部检测开始")
        print("  " + "=" * 70)

        # 1. 基础环境检测
        print("\n  📋 步骤 1/6: 基础环境检测")
        print("  " + "-" * 50)
        env_checker = EnvChecker()
        env_result = env_checker.check()
        env_checker.print_result(env_result)
        results.append(("基础环境检测", env_result.success))

        # 2. 依赖检测
        print("\n  📋 步骤 2/6: 依赖检测")
        print("  " + "-" * 50)
        deps_checker = DepsChecker()
        deps_result = deps_checker.check()
        deps_checker.print_result(deps_result)
        results.append(("依赖检测", deps_result.success))

        # 3. API密钥检测
        print("\n  📋 步骤 3/6: API密钥检测")
        print("  " + "-" * 50)
        api_result = self.run_api_key_check()
        from tests.checkers import APIChecker
        api_checker = APIChecker(test_connectivity=False)
        api_checker.print_result(api_result['result'])
        results.append(("API密钥检测", api_result['result'].success))

        # 4. API连通性测试
        print("\n  📋 步骤 4/6: API连通性测试")
        print("  " + "-" * 50)
        connectivity_result = self.run_connectivity_test()
        from tests.checkers import APIChecker
        connectivity_checker = APIChecker(test_connectivity=True)
        connectivity_checker.print_result(connectivity_result['result'])
        results.append(("API连通性测试", connectivity_result['result'].success))

        # 5. 功能测试
        print("\n  📋 步骤 5/6: 功能测试")
        print("  " + "-" * 50)
        function_result = self.run_function_test()
        # 功能测试只要有配置就算成功
        function_success = function_result.get('configured_providers', []) != []
        if function_success:
            print("  ✅ 功能测试环境就绪")
        else:
            print("  ❌ 功能测试环境未就绪")
        results.append(("功能测试", function_success))

        # 6. 可用模型检查
        print("\n  📋 步骤 6/6: 可用模型检查")
        print("  " + "-" * 50)
        models_result = self.show_available_models()
        if models_result['success']:
            print("  ✅ 模型配置加载成功")
        else:
            print("  ❌ 模型配置加载失败")
        results.append(("可用模型检查", models_result['success']))

        return {
            'check_results': results
        }
