"""
本地环境检测工具的UI显示模块
将UI逻辑从 check_local.py 中分离出来
"""

from typing import Dict, Any


class LocalUI:
    """本地环境检测工具UI"""

    @staticmethod
    def print_banner():
        """打印欢迎信息"""
        print()
        print("=" * 60)
        print("  🖥️  本地环境检测工具")
        print("=" * 60)
        print()
        print("  适用环境: Windows / macOS 开发机")
        print("  运行模式: 云API模式（调用远程API处理图片）")
        print()
        print("  本模式可以做什么：")
        print("  ✓ 调用阿里云、豆包、腾讯等云平台的多模态API")
        print("  ✓ 批量处理图片并提取结构化信息")
        print("  ✓ 无需GPU，只需网络连接和API密钥")
        print()
        print("=" * 60)

    @staticmethod
    def print_menu():
        """打印菜单"""
        print()
        print("  请选择操作：")
        print()
        print("  [1] 🔥 全部检测（推荐）")
        print("      依次运行所有检测，生成完整报告")
        print()
        print("  [2] 🔍 完整环境检测")
        print("      检测Python、依赖、配置文件、API密钥")
        print()
        print("  [3] 🔑 API密钥检测")
        print("      检测各云平台API密钥配置状态")
        print()
        print("  [4] 🌐 API连通性测试")
        print("      测试已配置的API是否能正常连接")
        print()
        print("  [5] 🧪 功能测试")
        print("      使用测试图片验证完整处理流程")
        print()
        print("  [6] 📋 查看可用模型")
        print("      列出所有已配置的云API模型")
        print()
        print("  [7] 🔧 问题诊断")
        print("      扫描常见问题并给出修复建议")
        print()
        print("  [0] 退出")
        print()

    @staticmethod
    def print_full_check_result(results: Dict[str, Any]):
        """打印完整检测结果"""
        print()
        print("  " + "=" * 56)
        print("  🔍 完整环境检测")
        print("  " + "=" * 56)

        # 打印各项检测结果
        check_names = {
            'env': '基础环境检测',
            'deps': '依赖检测',
            'api': 'API密钥检测'
        }

        for check_key, check_name in check_names.items():
            if check_key in results['checks']:
                print()
                print(f"  📌 {check_name}")
                print("  " + "─" * 56)
                # 使用checker的print_result方法
                result = results['checks'][check_key]
                if check_key == 'env':
                    from tests.checkers import EnvChecker
                    EnvChecker().print_result(result)
                elif check_key == 'deps':
                    from tests.checkers import DepsChecker
                    DepsChecker(check_local_model=False).print_result(result)
                elif check_key == 'api':
                    from tests.checkers import APIChecker
                    APIChecker(test_connectivity=False).print_result(result)

        # 汇总结果
        print()
        print("  " + "=" * 56)
        if results['all_passed']:
            print("  ✅ 环境检测通过！可以正常使用云API模式")
            print()
            print("  💡 下一步：")
            print("     python run_cli.py --select")
            print("     python run_web.py")
        else:
            print("  ❌ 环境检测发现问题")
            if results['fix_suggestions']:
                for fix in results['fix_suggestions']:
                    fix.print_suggestion()
        print("  " + "=" * 56)

    @staticmethod
    def print_api_key_check_result(api_data: Dict[str, Any]):
        """打印API密钥检测结果"""
        print()
        print("  " + "=" * 56)
        print("  🔑 API密钥检测")
        print("  " + "=" * 56)
        print()

        from tests.checkers import APIChecker
        checker = APIChecker(test_connectivity=False)
        checker.print_result(api_data['result'])

        # 显示未配置的API修复建议
        if api_data['fix_suggestions']:
            print()
            print("  💡 配置方法：")
            for fix in api_data['fix_suggestions']:
                fix.print_suggestion()

        print()
        print("  " + "=" * 56)

    @staticmethod
    def print_connectivity_test_result(connectivity_data: Dict[str, Any]):
        """打印API连通性测试结果"""
        print()
        print("  " + "=" * 56)
        print("  🌐 API连通性测试")
        print("  " + "=" * 56)
        print()
        print("  正在测试各平台连通性，请稍候...")
        print()

        from tests.checkers import APIChecker
        checker = APIChecker(test_connectivity=True)
        checker.print_result(connectivity_data['result'])

        print()
        print("  " + "=" * 56)

    @staticmethod
    def print_function_test_result(function_data: Dict[str, Any]):
        """打印功能测试结果"""
        print()
        print("  " + "=" * 56)
        print("  🧪 功能测试")
        print("  " + "=" * 56)

        # 检查测试图片目录
        if not function_data['dir_exists']:
            print()
            print("  ❌ 测试图片目录不存在")
            print(f"     路径: {function_data['test_images_dir']}")
            print()
            print("  💡 请将测试图片放入 data/inputs/ 目录")
            print()
            print("  " + "=" * 56)
            return

        if function_data['images_count'] == 0:
            print()
            print("  ❌ 测试图片目录为空")
            print()
            print("  💡 请将测试图片放入 data/inputs/ 目录")
            print()
            print("  " + "=" * 56)
            return

        print()
        print(f"  📸 找到 {function_data['images_count']} 张测试图片")
        if function_data['first_image']:
            print(f"     第一张: {function_data['first_image']}")

        # 检查API配置
        configured = function_data['configured_providers']
        if not configured:
            print()
            print("  ❌ 未配置任何API密钥，无法进行功能测试")
            print()
            print("  💡 请先配置API密钥，运行选项 [2] 查看详情")
            print()
            print("  " + "=" * 56)
            return

        print(f"  🔑 已配置的云平台: {', '.join(configured)}")
        print()
        print("  💡 运行功能测试命令：")
        print()
        print("     python run_cli.py --select")
        print()
        print("  " + "=" * 56)

    @staticmethod
    def print_available_models_result(models_data: Dict[str, Any]):
        """打印可用模型结果"""
        print()
        print("  " + "=" * 56)
        print("  📋 可用云API模型")
        print("  " + "=" * 56)

        if not models_data['success']:
            print(f"\n  ❌ 加载模型配置失败: {models_data['error']}")
            print()
            print("  " + "=" * 56)
            return

        for provider_key, provider_info in models_data['models_info'].items():
            models = provider_info['models']
            print()
            print(f"  🏢 {provider_info['display_name']}")
            print(f"     环境变量: {provider_info['env_key']}")
            print(f"     模型数量: {len(models)}")
            print("     " + "─" * 40)

            for model_key, model_info in list(models.items())[:3]:
                print(f"       • {model_info.get('label', model_key)}")

            if len(models) > 3:
                print(f"       ... 还有 {len(models) - 3} 个模型")

        print()
        print("  " + "=" * 56)

    @staticmethod
    def print_diagnosis_result(diagnosis_data: Dict[str, Any]):
        """打印问题诊断结果"""
        print()
        print("  " + "=" * 56)
        print("  🔧 问题诊断")
        print("  " + "=" * 56)

        print()
        print("  ⏳ 正在扫描常见问题...")
        print()
        print("  " + "─" * 56)

        if not diagnosis_data['has_issues']:
            print()
            print("  ✅ 未发现问题！环境配置正常")
            print()
            print("  💡 可以开始使用：")
            print("     python run_cli.py --select")
            print("     python run_web.py")
        else:
            issues = diagnosis_data['issues']
            print()
            print(f"  ❌ 发现 {len(issues)} 类问题：")

            for issue_name, fix in diagnosis_data['fix_suggestions']:
                print()
                print(f"  📌 {issue_name}")
                print("  " + "─" * 40)
                fix.print_suggestion()

        print()
        print("  " + "=" * 56)

    @staticmethod
    def print_full_local_check_result(results: Dict[str, Any]):
        """打印本地环境全部检测结果"""
        print()
        print("  " + "=" * 70)
        print("  🔥 本地环境全部检测报告")
        print("  " + "=" * 70)

        # 显示各项检测结果
        check_results = results.get('check_results', [])
        passed = sum(1 for _, success in check_results if success)
        total = len(check_results)

        print()
        for name, success in check_results:
            icon = "✅" if success else "❌"
            print(f"    {icon} {name}")

        print()
        print("  " + "-" * 70)

        if passed == total:
            print(f"    🎉 全部通过 ({passed}/{total})")
            print("    💡 本地环境配置完善，可以正常使用云API模式")
            print()
            print("    🚀 推荐下一步操作：")
            print("       python run_cli.py --select    # 命令行批处理")
            print("       python run_web.py             # Web管理界面")
        else:
            print(f"    ⚠️  部分通过 ({passed}/{total})")
            print("    💡 请查看上方详细信息，解决相关问题")

        print("  " + "=" * 70)
