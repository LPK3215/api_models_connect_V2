#!/usr/bin/env python3
"""
交互式检测工具 - 提供菜单选择不同的检测项目
适合需要选择性检测或详细了解各项检测结果的场景
"""

import io
import sys
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_banner():
    """打印横幅"""
    print()
    print("=" * 70)
    print("  🔍 交互式系统检测")
    print("=" * 70)
    print()
    print("  📖 说明: 提供菜单选择，可以单独运行各项检测")
    print("  💡 提示: 如需快速检测，请使用 python check_auto.py")
    print()


def print_menu():
    """打印菜单"""
    print("  请选择检测类型：")
    print()
    print("  [1] 🏗️  项目代码检测")
    print("      检查语法、目录结构、配置文件、模块导入")
    print()
    print("  [2] 💻 本地开发环境检测")
    print("      检查云API模式环境（Windows/macOS开发机）")
    print()
    print("  [3] ☁️  云服务器环境检测")
    print("      检查本地模型模式环境（GPU云服务器）")
    print()
    print("  [4] 🧪 基础系统测试")
    print("      运行所有基础测试和模块导入测试")
    print()
    print("  [5] 🔥 全面检测（推荐）")
    print("      依次运行所有检测，生成完整报告")
    print()
    print("  [0] 退出")
    print()


def run_project_check():
    """运行项目代码检测"""
    print()
    print("=" * 50)
    print("🏗️  项目代码检测")
    print("=" * 50)

    try:
        import subprocess
        result = subprocess.run([sys.executable, "tests/check_project.py"],
                                capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 项目检测失败: {e}")
        return False


def run_local_check():
    """运行本地环境检测"""
    print()
    print("=" * 50)
    print("💻 本地开发环境检测")
    print("=" * 50)

    try:
        from tests.checkers.local_checker import LocalEnvironmentChecker
        from tests.checkers.local_ui import LocalUI

        checker = LocalEnvironmentChecker()
        ui = LocalUI()

        results = checker.run_all_checks()
        ui.print_full_local_check_result(results)

        check_results = results.get('check_results', [])
        return all(success for _, success in check_results)

    except Exception as e:
        print(f"❌ 本地环境检测失败: {e}")
        return False


def run_cloud_check():
    """运行云服务器检测"""
    print()
    print("=" * 50)
    print("☁️  云服务器环境检测")
    print("=" * 50)

    try:
        from tests.checkers.cloud_checker import CloudEnvironmentChecker
        from tests.checkers.cloud_ui import CloudUI

        checker = CloudEnvironmentChecker()
        ui = CloudUI()

        results = checker.run_all_checks()
        ui.print_full_cloud_check_result(results)

        check_results = results.get('check_results', [])
        return all(success for _, success in check_results)

    except Exception as e:
        print(f"❌ 云服务器检测失败: {e}")
        return False


def run_system_test():
    """运行系统测试"""
    print()
    print("=" * 50)
    print("🧪 基础系统测试")
    print("=" * 50)

    try:
        import subprocess
        result = subprocess.run([sys.executable, "tests/test_all.py"],
                                capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 系统测试失败: {e}")
        return False


def run_full_check():
    """运行全面检测"""
    print()
    print("=" * 70)
    print("🔥 全面检测开始")
    print("=" * 70)

    results = []

    # 1. 项目代码检测
    print("\n📋 步骤 1/4: 项目代码检测")
    print("-" * 50)
    project_ok = run_project_check()
    results.append(("项目代码检测", project_ok))

    # 2. 系统测试
    print("\n📋 步骤 2/4: 基础系统测试")
    print("-" * 50)
    system_ok = run_system_test()
    results.append(("基础系统测试", system_ok))

    # 3. 本地环境检测
    print("\n📋 步骤 3/4: 本地环境检测")
    print("-" * 50)
    local_ok = run_local_check()
    results.append(("本地环境检测", local_ok))

    # 4. 云服务器检测
    print("\n📋 步骤 4/4: 云服务器检测")
    print("-" * 50)
    cloud_ok = run_cloud_check()
    results.append(("云服务器检测", cloud_ok))

    # 生成报告
    print_full_report(results)

    return all(success for _, success in results)


def print_full_report(results):
    """打印完整报告"""
    print()
    print("=" * 70)
    print("📊 全面检测报告")
    print("=" * 70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print()
    for name, success in results:
        icon = "✅" if success else "❌"
        print(f"  {icon} {name}")

    print()
    print("-" * 70)

    if passed == total:
        print(f"  🎉 全部通过 ({passed}/{total})")
        print("  💡 系统状态良好，可以正常使用")
    else:
        print(f"  ⚠️  部分通过 ({passed}/{total})")
        print("  💡 请查看上方详细信息，解决相关问题")

    print("=" * 70)


def main():
    """主函数"""
    print_banner()

    while True:
        print_menu()

        try:
            choice = input("  请输入选项 [0-5]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  👋 再见！")
            return 0

        if choice == "0":
            print("\n  👋 再见！")
            return 0
        elif choice == "1":
            success = run_project_check()
        elif choice == "2":
            success = run_local_check()
        elif choice == "3":
            success = run_cloud_check()
        elif choice == "4":
            success = run_system_test()
        elif choice == "5":
            success = run_full_check()
        else:
            print("\n  ⚠️  无效选项，请重新输入")
            continue

        # 询问是否继续
        print("\n" + "-" * 50)
        try:
            continue_choice = input("按回车键返回主菜单，或输入 'q' 退出: ").strip().lower()
            if continue_choice == 'q':
                print("\n  👋 再见！")
                return 0
        except (EOFError, KeyboardInterrupt):
            print("\n\n  👋 再见！")
            return 0


if __name__ == "__main__":
    sys.exit(main())
