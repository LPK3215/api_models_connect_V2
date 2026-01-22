#!/usr/bin/env python3
"""
项目健康检查工具
检测模块导入、文件依赖、语法错误等
"""

import ast
import importlib
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

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))


def print_header(title: str):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    print()
    print(f"  📌 {title}")
    print("  " + "─" * 56)


def check_syntax_errors():
    """检查所有Python文件的语法错误"""
    print_section("语法检查")

    errors = []
    py_files = list(PROJECT_ROOT.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f) and ".venv" not in str(f)]

    for py_file in py_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source)
        except SyntaxError as e:
            errors.append((py_file, e))
        except Exception as e:
            errors.append((py_file, e))

    if errors:
        for py_file, error in errors:
            rel_path = py_file.relative_to(PROJECT_ROOT)
            print(f"     ❌ {rel_path}")
            print(f"        {error}")
        return False
    else:
        print(f"     ✅ {len(py_files)} 个文件语法正确")
        return True


def check_module_imports():
    """检查核心模块是否能正常导入"""
    print_section("模块导入检查")

    modules = [
        ("backend.core.config", "全局配置"),
        ("backend.core.config_loader", "配置加载器"),
        ("backend.core.processor", "处理器"),
        ("backend.core.cli", "CLI模块"),
        ("backend.core.local", "云API处理模块"),
        ("backend.app", "FastAPI 应用"),
        ("tests.checkers", "检测器模块"),
        ("tests.fixers", "修复器模块"),
    ]

    success = True
    for module_name, display_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"     ✅ {display_name} ({module_name})")
        except Exception as e:
            print(f"     ❌ {display_name} ({module_name})")
            print(f"        错误: {e}")
            success = False

    return success


def check_import_dependencies():
    """分析文件间的导入依赖关系"""
    print_section("导入依赖分析")

    src_files = list((PROJECT_ROOT / "src" / "backend").rglob("*.py"))
    src_files = [f for f in src_files if "__pycache__" not in str(f)]

    dependencies = {}
    errors = []

    for py_file in src_files:
        rel_path = py_file.relative_to(PROJECT_ROOT)
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # 只保留项目内部导入
            internal_imports = [i for i in imports if i.startswith(("backend.", "tests."))]
            dependencies[str(rel_path)] = internal_imports

        except Exception as e:
            errors.append((rel_path, e))

    # 检查是否有循环依赖或无效导入
    print(f"     📊 分析了 {len(src_files)} 个源文件")

    # 显示主要模块的依赖
    key_modules = ["src/backend/core/processor.py", "src/backend/core/cli.py", "src/backend/core/local/__init__.py"]
    for module in key_modules:
        if module in dependencies:
            deps = dependencies[module]
            if deps:
                print(f"     📦 {module} -> {', '.join(deps[:3])}{'...' if len(deps) > 3 else ''}")

    if errors:
        for rel_path, error in errors:
            print(f"     ❌ {rel_path}: {error}")
        return False

    return True


def check_config_files():
    """检查配置文件是否存在且有效"""
    print_section("配置文件检查")

    config_files = [
        ("config/models.yml", "模型配置"),
        ("config/prompts/default.yml", "默认提示词"),
        ("pyproject.toml", "项目配置"),
        ("requirements.txt", "依赖列表"),
    ]

    success = True
    for file_path, display_name in config_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"     ✅ {display_name} ({file_path}) - {size} bytes")
        else:
            print(f"     ❌ {display_name} ({file_path}) - 不存在")
            success = False

    return success


def check_directory_structure():
    """检查目录结构是否完整"""
    print_section("目录结构检查")

    required_dirs = [
        "src/backend",
        "src/backend/core",
        "src/backend/core/local",
        "src/backend/routes",
        "src/backend/services",
        "scripts",
        "tests",
        "tests/checkers",
        "tests/fixers",
        "config",
        "config/prompts",
        "data/inputs",
        "data/outputs",
    ]

    success = True
    for dir_path in required_dirs:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists() and full_path.is_dir():
            file_count = len(list(full_path.glob("*.py")))
            print(f"     ✅ {dir_path}/ ({file_count} py文件)")
        else:
            print(f"     ❌ {dir_path}/ - 不存在")
            success = False

    return success


def check_entry_points():
    """检查入口文件是否可执行"""
    print_section("入口文件检查")

    entry_points = [
        ("run_api.py", "后端 API 入口"),
        ("run_cli.py", "CLI入口"),
        ("src/backend/run.py", "后端 Runner (包内)"),
        ("tests/check_cloud.py", "云API检测"),
    ]

    success = True
    for file_path, display_name in entry_points:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            # 尝试编译检查
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    source = f.read()
                compile(source, file_path, "exec")
                print(f"     ✅ {display_name} ({file_path})")
            except SyntaxError as e:
                print(f"     ❌ {display_name} ({file_path}) - 语法错误: {e}")
                success = False
        else:
            print(f"     ❌ {display_name} ({file_path}) - 不存在")
            success = False

    return success


def run_quick_test():
    """运行快速功能测试"""
    print_section("快速功能测试")

    tests = []

    # 测试1: 配置加载
    try:
        from backend.core.config_loader import get_providers
        providers = get_providers()
        tests.append(("配置加载", True, f"{len(providers)} 个提供商"))
    except Exception as e:
        tests.append(("配置加载", False, str(e)))

    # 测试2: 处理器导入
    try:
        from backend.core.processor import run_pipeline, Processor
        tests.append(("处理器", True, "run_pipeline, Processor"))
    except Exception as e:
        tests.append(("处理器", False, str(e)))

    # 测试3: 云API模块
    try:
        from backend.core.local import get_image_url, process_images_with_cloud_api
        tests.append(("云API模块", True, "云API处理"))
    except Exception as e:
        tests.append(("云API模块", False, str(e)))

    # 测试4: FastAPI 应用
    try:
        from backend.app import create_app
        tests.append(("FastAPI 应用", True, "create_app"))
    except Exception as e:
        tests.append(("FastAPI 应用", False, str(e)))

    success = True
    for name, passed, detail in tests:
        if passed:
            print(f"     ✅ {name}: {detail}")
        else:
            print(f"     ❌ {name}: {detail}")
            success = False

    return success


def main():
    print_header("🔍 项目健康检查")

    results = []

    results.append(("语法检查", check_syntax_errors()))
    results.append(("目录结构", check_directory_structure()))
    results.append(("配置文件", check_config_files()))
    results.append(("入口文件", check_entry_points()))
    results.append(("模块导入", check_module_imports()))
    results.append(("依赖分析", check_import_dependencies()))
    results.append(("功能测试", run_quick_test()))

    # 汇总
    print_header("📊 检查汇总")
    print()

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        icon = "✅" if ok else "❌"
        print(f"     {icon} {name}")

    print()
    print("  " + "─" * 56)

    if passed == total:
        print(f"  ✅ 全部通过 ({passed}/{total})")
        print()
        print("  💡 项目状态良好，可以正常使用")
        return 0
    else:
        print(f"  ⚠️ 部分检查未通过 ({passed}/{total})")
        print()
        print("  💡 请根据上述错误信息修复问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())
