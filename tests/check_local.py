#!/usr/bin/env python3
"""
本地环境检测入口
适用于：Windows/macOS 开发机，使用云API模式
"""

import io
import sys
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.checkers.local_checker import LocalEnvironmentChecker
from tests.checkers.local_ui import LocalUI


def main():
    """主函数"""
    ui = LocalUI()
    checker = LocalEnvironmentChecker()

    ui.print_banner()

    while True:
        ui.print_menu()

        try:
            choice = input("  请输入选项 [0-7]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  👋 再见！")
            break

        if choice == "0":
            print("\n  👋 再见！")
            break
        elif choice == "1":
            # 全部检测
            results = checker.run_all_checks()
            ui.print_full_local_check_result(results)
        elif choice == "2":
            results = checker.run_full_check()
            ui.print_full_check_result(results)
        elif choice == "3":
            api_data = checker.run_api_key_check()
            ui.print_api_key_check_result(api_data)
        elif choice == "4":
            connectivity_data = checker.run_connectivity_test()
            ui.print_connectivity_test_result(connectivity_data)
        elif choice == "5":
            function_data = checker.run_function_test()
            ui.print_function_test_result(function_data)
        elif choice == "6":
            models_data = checker.show_available_models()
            ui.print_available_models_result(models_data)
        elif choice == "7":
            diagnosis_data = checker.run_diagnosis()
            ui.print_diagnosis_result(diagnosis_data)
        else:
            print("\n  ⚠️ 无效选项，请重新输入")

        input("\n  按回车键继续...")


if __name__ == "__main__":
    main()
