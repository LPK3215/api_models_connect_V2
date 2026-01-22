#!/usr/bin/env python3
"""
云API环境检测入口
检测云API调用所需的环境配置
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
src_root = project_root / "src"
sys.path.insert(0, str(src_root))
sys.path.insert(0, str(project_root))

from tests.checkers.cloud_checker import CloudEnvironmentChecker


def main():
    """主函数"""
    checker = CloudEnvironmentChecker()

    print()
    print("=" * 70)
    print("  🔥 云API环境检测")
    print("=" * 70)

    while True:
        print()
        print("  请选择检测项目:")
        print("  " + "-" * 50)
        print("  1. 运行全部检测")
        print("  2. 查看云端模型配置")
        print("  3. 运行问题诊断")
        print("  0. 退出")
        print()

        try:
            choice = input("  请输入选项 [0-3]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  👋 再见！")
            break

        if choice == "0":
            print("\n  👋 再见！")
            break
        elif choice == "1":
            # 全部检测
            results = checker.run_all_checks()
            _print_check_results(results)
        elif choice == "2":
            # 查看云端模型
            models_data = checker.show_cloud_models()
            _print_models(models_data)
        elif choice == "3":
            # 问题诊断
            diagnosis_data = checker.run_diagnosis()
            _print_diagnosis(diagnosis_data)
        else:
            print("\n  ⚠️ 无效选项，请重新输入")

        input("\n  按回车键继续...")


def _print_check_results(results):
    """打印检测结果"""
    print()
    print("  " + "=" * 60)
    print("  📊 检测结果汇总")
    print("  " + "=" * 60)
    
    check_results = results.get('check_results', [])
    passed = sum(1 for _, ok in check_results if ok)
    total = len(check_results)
    
    for name, ok in check_results:
        icon = "✅" if ok else "❌"
        print(f"  {icon} {name}")
    
    print()
    if passed == total:
        print(f"  ✅ 全部通过 ({passed}/{total})")
    else:
        print(f"  ⚠️ 部分未通过 ({passed}/{total})")


def _print_models(models_data):
    """打印模型配置"""
    print()
    print("  " + "=" * 60)
    print("  📦 云端模型配置")
    print("  " + "=" * 60)
    
    if not models_data.get('success'):
        print(f"  ❌ 加载失败: {models_data.get('error')}")
        return
    
    models_info = models_data.get('models_info', {})
    for provider_key, provider_data in models_info.items():
        display_name = provider_data.get('display_name', provider_key)
        models = provider_data.get('models', {})
        print(f"\n  📌 {display_name} ({len(models)} 个模型)")
        for model_key in list(models.keys())[:3]:
            print(f"     - {model_key}")
        if len(models) > 3:
            print(f"     ... 还有 {len(models) - 3} 个模型")


def _print_diagnosis(diagnosis_data):
    """打印诊断结果"""
    print()
    print("  " + "=" * 60)
    print("  🔍 问题诊断")
    print("  " + "=" * 60)
    
    if not diagnosis_data.get('has_issues'):
        print("  ✅ 未发现问题")
        return
    
    issues = diagnosis_data.get('issues', [])
    for issue_name, result in issues:
        print(f"\n  ❌ {issue_name}: {result.message}")
    
    fix_suggestions = diagnosis_data.get('fix_suggestions', [])
    if fix_suggestions:
        print("\n  💡 修复建议:")
        for issue_name, fix in fix_suggestions:
            print(f"     - {fix.title}: {fix.description}")


if __name__ == "__main__":
    main()
