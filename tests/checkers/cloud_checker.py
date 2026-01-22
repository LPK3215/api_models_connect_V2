"""
云服务器环境检测核心模块
将检测逻辑从 check_cloud.py 中分离出来
"""

import sys
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class CloudEnvironmentChecker:
    """云服务器环境检测器（仅API模式）"""

    def __init__(self):
        self.project_root = project_root

    def run_full_check(self) -> Dict[str, Any]:
        """运行完整环境检测"""
        from tests.checkers import EnvChecker, DepsChecker, PathChecker, APIChecker
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

        # 3. 路径检测
        path_checker = PathChecker()
        path_result = path_checker.check()
        results['checks']['path'] = path_result
        if not path_result.success:
            results['all_passed'] = False
            env_fixer = EnvFixer()
            for sub in path_result.sub_results:
                if not sub.success and sub.fix_key:
                    fix = env_fixer.get_fix(sub.fix_key)
                    if fix:
                        results['fix_suggestions'].append(fix)

        # 4. API检测
        api_checker = APIChecker()
        api_result = api_checker.check()
        results['checks']['api'] = api_result

        return results

    def run_api_check(self) -> Dict[str, Any]:
        """运行API检测"""
        from tests.checkers import APIChecker

        checker = APIChecker()
        result = checker.check()

        return {
            'result': result,
            'fix_suggestion': None
        }

    def run_path_check(self) -> Dict[str, Any]:
        """运行路径检测"""
        from tests.checkers import PathChecker
        from tests.fixers import EnvFixer

        checker = PathChecker()
        result = checker.check()

        return {
            'result': result,
            'fix_suggestions': [
                EnvFixer().get_fix(sub.fix_key)
                for sub in result.sub_results
                if not sub.success and sub.fix_key
            ]
        }

    def show_cloud_models(self) -> Dict[str, Any]:
        """显示云端模型配置"""
        try:
            from src.config_loader import get_providers
            providers = get_providers()

            models_info = {}
            for provider_key, provider_data in providers.items():
                info = provider_data.get("info", {})
                models = provider_data.get("model_pool", {})

                models_info[provider_key] = {
                    'display_name': info.get('display_name', provider_key),
                    'models': models
                }

            return {'success': True, 'models_info': models_info}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def run_diagnosis(self) -> Dict[str, Any]:
        """运行问题诊断"""
        from tests.checkers import EnvChecker, DepsChecker, PathChecker, APIChecker
        from tests.fixers import DepsFixer, EnvFixer, ConfigFixer

        issues = []

        # 检测各项
        checkers = [
            ("环境问题", EnvChecker()),
            ("依赖问题", DepsChecker()),
            ("路径问题", PathChecker()),
            ("API问题", APIChecker())
        ]

        for issue_name, checker in checkers:
            result = checker.check()
            if not result.success:
                issues.append((issue_name, result))

        # 生成修复建议
        fixers = [DepsFixer(), EnvFixer(), ConfigFixer()]
        fix_suggestions = []

        for issue_name, result in issues:
            if result.fix_key:
                for fixer in fixers:
                    fix = fixer.get_fix(result.fix_key)
                    if fix:
                        fix_suggestions.append((issue_name, fix))
                        break

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
        from tests.checkers import EnvChecker, DepsChecker, PathChecker, APIChecker

        results = []

        print()
        print("  " + "=" * 70)
        print("  🔥 云API环境检测开始")
        print("  " + "=" * 70)

        # 1. 基础环境检测
        print("\n  📋 步骤 1/4: 基础环境检测")
        print("  " + "-" * 50)
        env_checker = EnvChecker()
        env_result = env_checker.check()
        env_checker.print_result(env_result)
        results.append(("基础环境检测", env_result.success))

        # 2. 依赖检测
        print("\n  📋 步骤 2/4: 依赖检测")
        print("  " + "-" * 50)
        deps_checker = DepsChecker()
        deps_result = deps_checker.check()
        deps_checker.print_result(deps_result)
        results.append(("依赖检测", deps_result.success))

        # 3. 路径检测
        print("\n  📋 步骤 3/4: 路径检测")
        print("  " + "-" * 50)
        path_result = self.run_path_check()
        path_checker = PathChecker()
        path_checker.print_result(path_result['result'])
        results.append(("路径检测", path_result['result'].success))

        # 4. 云端模型配置检查
        print("\n  📋 步骤 4/4: 云端模型配置检查")
        print("  " + "-" * 50)
        models_result = self.show_cloud_models()
        models_info = models_result.get('models_info', {})
        models_success = models_result.get('success', False) and len(models_info) > 0
        if models_success:
            print("  ✅ 云端模型配置加载成功")
            print(f"  📊 已配置 {len(models_info)} 个云平台")
        else:
            print("  ❌ 云端模型配置加载失败")
        results.append(("云端模型配置检查", models_success))

        return {
            'check_results': results
        }
