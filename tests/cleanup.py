#!/usr/bin/env python3
"""
项目清理工具
清理临时文件、缓存、输出结果等
"""

import shutil
import sys
from pathlib import Path
from typing import List, Tuple

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


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent


def print_banner():
    """打印欢迎横幅"""
    print()
    print("=" * 60)
    print("  🧹 项目清理工具")
    print("=" * 60)
    print()
    print(f"  📁 项目目录: {get_project_root()}")
    print()


def print_menu():
    """打印菜单"""
    print()
    print("  请选择清理选项：")
    print()
    print("  [1] 🗑️ 清理 __pycache__ 缓存")
    print("  [2] 📤 清理输出结果 (data/outputs)")
    print("  [3] 📄 清理临时文件 (*.pyc, *.log 等)")
    print("  [4] ⚙️ 清理配置缓存 (任务历史等)")
    print("  [5] 🔥 全部清理")
    print()
    print("  [0] 退出")
    print()


def confirm_action(message: str) -> bool:
    """确认操作"""
    print()
    print(f"  ⚠️  {message}")
    try:
        response = input("  确认执行? (y/N): ").strip().lower()
        return response in ['y', 'yes', '是']
    except (KeyboardInterrupt, EOFError):
        return False


def scan_pycache(project_root: Path) -> List[Path]:
    """扫描 __pycache__ 目录"""
    return [p for p in project_root.rglob("__pycache__") if p.is_dir()]


def clean_pycache(project_root: Path) -> Tuple[int, int]:
    """清理 __pycache__ 目录"""
    items = scan_pycache(project_root)
    cleaned = 0
    for pycache in items:
        try:
            shutil.rmtree(pycache)
            cleaned += 1
        except Exception:
            pass
    return cleaned, len(items)


def scan_outputs(project_root: Path) -> List[Path]:
    """扫描输出目录"""
    outputs_dir = project_root / "data" / "outputs"
    if not outputs_dir.exists():
        return []
    return [d for d in outputs_dir.iterdir() if d.is_dir()]


def clean_outputs(project_root: Path, keep_recent: int = 0) -> Tuple[int, int]:
    """清理输出目录"""
    items = scan_outputs(project_root)
    if not items:
        return 0, 0

    # 按修改时间排序
    items_sorted = sorted(items, key=lambda x: x.stat().st_mtime, reverse=True)

    # 保留最近的N个
    to_remove = items_sorted[keep_recent:] if keep_recent > 0 else items_sorted

    cleaned = 0
    for d in to_remove:
        try:
            shutil.rmtree(d)
            cleaned += 1
        except Exception:
            pass

    return cleaned, len(items)


def scan_temp_files(project_root: Path) -> List[Path]:
    """扫描临时文件"""
    # 安全的文件扩展名模式（不会误删系统文件）
    safe_patterns = ["*.pyc", "*.pyo", "*.log", ".DS_Store", "Thumbs.db", "*.tmp"]
    files = []

    # 排除的目录（绝对不能清理）
    excluded_dirs = {".venv", "venv", "env", "site-packages", "node_modules", ".git"}

    for pattern in safe_patterns:
        for file_path in project_root.rglob(pattern):
            if file_path.is_file():
                # 检查路径中是否包含排除的目录
                if not any(excluded in str(file_path) for excluded in excluded_dirs):
                    files.append(file_path)

    # 只在项目根目录下查找临时Python文件（更安全）
    project_temp_patterns = ["temp_*.py", "tmp_*.py", "test_temp_*.py"]
    for pattern in project_temp_patterns:
        # 只在项目根目录和src目录下查找，避免误删依赖包文件
        search_dirs = [project_root, project_root / "src", project_root / "tests"]
        for search_dir in search_dirs:
            if search_dir.exists():
                for file_path in search_dir.glob(pattern):
                    if file_path.is_file():
                        files.append(file_path)

    return files


def clean_temp_files(project_root: Path) -> Tuple[int, int]:
    """清理临时文件"""
    items = scan_temp_files(project_root)
    cleaned = 0
    for f in items:
        try:
            f.unlink()
            cleaned += 1
        except Exception:
            pass
    return cleaned, len(items)


def scan_config_cache(project_root: Path) -> List[Path]:
    """扫描配置缓存"""
    files = []
    cache_files = [
        project_root / "config" / "task_history.json",
        project_root / "config" / "last_choice.json",
    ]
    for f in cache_files:
        if f.exists():
            files.append(f)
    return files


def clean_config_cache(project_root: Path) -> Tuple[int, int]:
    """清理配置缓存"""
    items = scan_config_cache(project_root)
    cleaned = 0
    for f in items:
        try:
            f.unlink()
            cleaned += 1
        except Exception:
            pass
    return cleaned, len(items)


def print_scan_result(title: str, items: List[Path], max_show: int = 5):
    """打印扫描结果"""
    print()
    print(f"  📋 {title}")
    print(f"  {'─' * 50}")

    if not items:
        print("     (无)")
        return

    for item in items[:max_show]:
        # 显示相对路径
        try:
            rel_path = item.relative_to(get_project_root())
        except ValueError:
            rel_path = item
        print(f"     • {rel_path}")

    if len(items) > max_show:
        print(f"     ... 还有 {len(items) - max_show} 项")

    print(f"  {'─' * 50}")
    print(f"  共 {len(items)} 项")


def print_clean_result(title: str, cleaned: int, total: int):
    """打印清理结果"""
    print()
    if cleaned == total and total > 0:
        print(f"  ✅ {title}: 已清理 {cleaned} 项")
    elif cleaned > 0:
        print(f"  ⚠️  {title}: 清理了 {cleaned}/{total} 项")
    elif total == 0:
        print(f"  ℹ️  {title}: 无需清理")
    else:
        print(f"  ❌ {title}: 清理失败")


def handle_pycache():
    """处理 __pycache__ 清理"""
    project_root = get_project_root()
    items = scan_pycache(project_root)

    print_scan_result("__pycache__ 缓存目录", items)

    if not items:
        return

    if confirm_action(f"将删除 {len(items)} 个 __pycache__ 目录"):
        cleaned, total = clean_pycache(project_root)
        print_clean_result("__pycache__ 缓存", cleaned, total)
    else:
        print("\n  ℹ️  已取消")


def handle_outputs():
    """处理输出结果清理"""
    project_root = get_project_root()
    items = scan_outputs(project_root)

    print_scan_result("输出结果目录", items)

    if not items:
        return

    print()
    print("  选择清理方式：")
    print("  [1] 全部清理")
    print("  [2] 保留最近 N 个")
    print("  [0] 取消")

    try:
        sub_choice = input("\n  请选择: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n  ℹ️  已取消")
        return

    if sub_choice == "0":
        print("\n  ℹ️  已取消")
        return
    elif sub_choice == "1":
        if confirm_action(f"将删除全部 {len(items)} 个输出目录"):
            cleaned, total = clean_outputs(project_root, keep_recent=0)
            print_clean_result("输出结果", cleaned, total)
        else:
            print("\n  ℹ️  已取消")
    elif sub_choice == "2":
        try:
            keep = int(input("  保留最近几个? ").strip())
            if keep < 0:
                keep = 0
        except (ValueError, KeyboardInterrupt, EOFError):
            print("\n  ℹ️  已取消")
            return

        to_delete = max(0, len(items) - keep)
        if to_delete == 0:
            print(f"\n  ℹ️  当前只有 {len(items)} 个，无需清理")
            return

        if confirm_action(f"将删除 {to_delete} 个旧输出目录，保留最近 {keep} 个"):
            cleaned, total = clean_outputs(project_root, keep_recent=keep)
            print_clean_result("输出结果", cleaned, total)
        else:
            print("\n  ℹ️  已取消")
    else:
        print("\n  ⚠️  无效选项")


def handle_temp_files():
    """处理临时文件清理"""
    project_root = get_project_root()
    items = scan_temp_files(project_root)

    print_scan_result("临时文件", items)

    if not items:
        return

    if confirm_action(f"将删除 {len(items)} 个临时文件"):
        cleaned, total = clean_temp_files(project_root)
        print_clean_result("临时文件", cleaned, total)
    else:
        print("\n  ℹ️  已取消")


def handle_config_cache():
    """处理配置缓存清理"""
    project_root = get_project_root()
    items = scan_config_cache(project_root)

    print_scan_result("配置缓存文件", items)

    if not items:
        return

    if confirm_action(f"将删除 {len(items)} 个配置缓存文件"):
        cleaned, total = clean_config_cache(project_root)
        print_clean_result("配置缓存", cleaned, total)
    else:
        print("\n  ℹ️  已取消")


def handle_all():
    """处理全部清理"""
    project_root = get_project_root()

    # 扫描所有
    pycache_items = scan_pycache(project_root)
    output_items = scan_outputs(project_root)
    temp_items = scan_temp_files(project_root)
    config_items = scan_config_cache(project_root)

    total_items = len(pycache_items) + len(output_items) + len(temp_items) + len(config_items)

    print()
    print("  📊 扫描结果汇总：")
    print(f"  {'─' * 50}")
    print(f"     __pycache__ 目录: {len(pycache_items)} 个")
    print(f"     输出结果目录:     {len(output_items)} 个")
    print(f"     临时文件:         {len(temp_items)} 个")
    print(f"     配置缓存:         {len(config_items)} 个")
    print(f"  {'─' * 50}")
    print(f"     总计: {total_items} 项")

    if total_items == 0:
        print("\n  ℹ️  无需清理")
        return

    if confirm_action(f"将清理以上全部 {total_items} 项"):
        results = []

        if pycache_items:
            c, t = clean_pycache(project_root)
            results.append(("__pycache__", c, t))

        if output_items:
            c, t = clean_outputs(project_root, keep_recent=0)
            results.append(("输出结果", c, t))

        if temp_items:
            c, t = clean_temp_files(project_root)
            results.append(("临时文件", c, t))

        if config_items:
            c, t = clean_config_cache(project_root)
            results.append(("配置缓存", c, t))

        print()
        print("  📊 清理结果：")
        print(f"  {'─' * 50}")
        total_cleaned = 0
        for name, cleaned, total in results:
            status = "✅" if cleaned == total else "⚠️"
            print(f"     {status} {name}: {cleaned}/{total}")
            total_cleaned += cleaned
        print(f"  {'─' * 50}")
        print(f"     总计清理: {total_cleaned} 项")
    else:
        print("\n  ℹ️  已取消")


def main():
    """主函数"""
    print_banner()

    while True:
        print_menu()

        try:
            choice = input("  请输入选项 [0-5]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  👋 再见！")
            break

        if choice == "0":
            print("\n  👋 再见！")
            break
        elif choice == "1":
            handle_pycache()
        elif choice == "2":
            handle_outputs()
        elif choice == "3":
            handle_temp_files()
        elif choice == "4":
            handle_config_cache()
        elif choice == "5":
            handle_all()
        else:
            print("\n  ⚠️  无效选项，请重新输入")

        input("\n  按回车键继续...")


if __name__ == "__main__":
    main()
