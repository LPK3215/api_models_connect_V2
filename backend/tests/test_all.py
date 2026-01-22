#!/usr/bin/env python3
"""
完整测试套件
整合所有检测器进行系统测试
"""

import sys
from pathlib import Path

# 避免 Windows 控制台(GBK)输出 Emoji 报 UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
src_root = project_root / "src"
sys.path.insert(0, str(src_root))
sys.path.insert(0, str(project_root))


def print_banner():
    """打印横幅"""
    print()
    print("=" * 60)
    print("  🧪 系统完整测试")
    print("=" * 60)
    print()


def run_basic_tests():
    """运行基础测试"""
    print("  📌 基础环境测试")
    print("  " + "─" * 56)

    from tests.checkers import EnvChecker, DepsChecker

    results = []

    # 环境检测
    env_checker = EnvChecker()
    env_result = env_checker.check()
    env_checker.print_result(env_result)
    results.append(("环境检测", env_result.success))

    # 依赖检测
    deps_checker = DepsChecker()
    deps_result = deps_checker.check()
    deps_checker.print_result(deps_result)
    results.append(("依赖检测", deps_result.success))

    return results


def run_api_tests():
    """运行API测试"""
    print()
    print("  📌 API配置测试")
    print("  " + "─" * 56)

    from tests.checkers import APIChecker

    results = []

    # API密钥检测
    api_checker = APIChecker(test_connectivity=False)
    api_result = api_checker.check()
    api_checker.print_result(api_result)
    results.append(("API密钥", api_result.success))

    return results


def run_config_tests():
    """运行配置测试"""
    print()
    print("  📌 配置文件测试")
    print("  " + "─" * 56)

    results = []

    # 检查配置文件
    config_files = [
        project_root / "config" / "models.yml",
        project_root / "config" / "prompts" / "default.yml",
    ]

    for config_file in config_files:
        if config_file.exists():
            print(f"     ✅ {config_file.name} 存在")
            results.append((config_file.name, True))
        else:
            print(f"     ❌ {config_file.name} 不存在")
            results.append((config_file.name, False))

    return results


def run_import_tests():
    """运行导入测试"""
    print()
    print("  📌 模块导入测试")
    print("  " + "─" * 56)

    results = []

    modules = [
        ("backend.core.config", "配置模块"),
        ("backend.core.config_loader", "配置加载器"),
        ("backend.core.processor", "处理器"),
        ("backend.core.cli", "CLI模块"),
        ("backend.app", "FastAPI 应用"),
    ]

    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"     ✅ {display_name} ({module_name})")
            results.append((display_name, True))
        except Exception as e:
            print(f"     ❌ {display_name} ({module_name})")
            print(f"        错误: {e}")
            results.append((display_name, False))

    return results


def print_summary(all_results):
    """打印测试汇总"""
    print()
    print("  " + "=" * 56)
    print("  📊 测试汇总")
    print("  " + "=" * 56)

    passed = sum(1 for _, success in all_results if success)
    total = len(all_results)

    print()
    for name, success in all_results:
        icon = "✅" if success else "❌"
        print(f"     {icon} {name}")

    print()
    print("  " + "─" * 56)

    if passed == total:
        print(f"  ✅ 全部通过 ({passed}/{total})")
    else:
        print(f"  ⚠️ 部分通过 ({passed}/{total})")

    print()
    print("  " + "=" * 56)

    return passed == total


def main():
    """主函数"""
    print_banner()

    all_results = []

    # 运行各项测试
    all_results.extend(run_basic_tests())
    all_results.extend(run_api_tests())
    all_results.extend(run_config_tests())
    all_results.extend(run_import_tests())

    # 打印汇总
    success = print_summary(all_results)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
