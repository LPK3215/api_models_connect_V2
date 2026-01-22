#!/usr/bin/env python3
"""
自动检测脚本 - 非交互式完整检测
运行所有检测并直接输出结果，适合快速验证系统状态
"""

import io
import sys
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录与 src 到路径
project_root = Path(__file__).resolve().parent.parent
src_root = project_root / "src"
sys.path.insert(0, str(src_root))
sys.path.insert(0, str(project_root))


def main():
    """主函数"""
    print()
    print("=" * 70)
    print("🔍 多模态批处理系统 - 自动检测")
    print("=" * 70)
    print()

    results = []

    # 1. 项目代码检测
    print("📋 [1/3] 项目代码检测")
    print("-" * 70)
    try:
        import subprocess
        result = subprocess.run([sys.executable, "tests/check_project.py"],
                                cwd=str(project_root), capture_output=False, text=True)
        results.append(("项目代码检测", result.returncode == 0))
    except Exception as e:
        print(f"❌ 检测失败: {e}")
        results.append(("项目代码检测", False))

    # 2. 基础测试
    print("\n📋 [2/3] 基础测试")
    print("-" * 70)
    try:
        result = subprocess.run([sys.executable, "tests/test_all.py"],
                                cwd=str(project_root), capture_output=False, text=True)
        results.append(("基础测试", result.returncode == 0))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results.append(("基础测试", False))

    # 3. 本地环境检测
    print("\n📋 [3/3] 本地环境检测")
    print("-" * 70)
    try:
        from tests.checkers.local_checker import LocalEnvironmentChecker
        from tests.checkers.local_ui import LocalUI

        checker = LocalEnvironmentChecker()
        ui = LocalUI()

        check_results = checker.run_all_checks()
        ui.print_full_local_check_result(check_results)

        all_passed = all(success for _, success in check_results.get('check_results', []))
        results.append(("本地环境检测", all_passed))
    except Exception as e:
        print(f"❌ 检测失败: {e}")
        results.append(("本地环境检测", False))

    # 生成报告
    print("\n" + "=" * 70)
    print("📊 检测报告")
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
        print()
        print("  💡 系统状态良好，所有功能可以正常使用！")
        print()
        print("  🚀 推荐下一步：")
        print("     python run_api.py           # 启动后端 API (FastAPI)")
        print("     cd ..\\frontend; npm run dev # 启动前端 (Vue)")
        print("     python run_cli.py --select  # 命令行批处理")
    else:
        print(f"  ⚠️  部分通过 ({passed}/{total})")
        print()
        print("  💡 请查看上方详细信息，解决相关问题")
        print()
        print("  🔧 获取帮助：")
        print("     python scripts/check_interactive.py  # 交互式检测（更多选项）")

    print("=" * 70)
    print()

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
