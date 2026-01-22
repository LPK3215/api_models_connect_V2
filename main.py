#!/usr/bin/env python3
"""
多模态批处理系统 - 主启动器
提供完整的项目管理和启动功能
"""

import subprocess
import sys
from pathlib import Path


def show_project_info():
    """显示项目信息"""
    print("\n" + "=" * 70)
    print("🚀 多模态批处理系统")
    print("=" * 70)
    print("📖 项目说明:")
    print("   一个现代化的多云平台图片批处理工具，支持阿里云、豆包、")
    print("   魔塔、腾讯混元等主流AI平台的视觉模型。")
    print()
    print("✨ 主要功能:")
    print("   🤖 多云平台支持 - 集成主流AI视觉模型")
    print("   🖼️  批量图片处理 - 支持多张图片同时处理")
    print("   📝 结构化信息抽取 - 提取JSON格式数据")
    print("   🌐 现代化Web界面 - 完整的管理系统")
    print("   💻 命令行支持 - 适合脚本化场景")
    print("   🧪 完整测试套件 - 验证系统配置")
    print()
    print("🤖 支持的AI平台:")
    print("   • 阿里云 DashScope (通义千问系列)")
    print("   • 豆包/火山方舟 Ark (豆包系列)")
    print("   • 魔塔 ModelScope (Qwen、InternVL等)")
    print("   • 腾讯混元大模型 (混元系列)")
    print("=" * 70)


def show_main_menu():
    """显示主菜单"""
    print("\n📋 请选择操作:")
    print()
    print("🚀 启动应用:")
    print("   1. 📱 Web管理系统 (推荐)")
    print("      - 完整的图形化管理界面")
    print("      - 模型管理、任务处理、提示词库等")
    print("      - 浏览器访问: http://127.0.0.1:8080")
    print()
    print("   2. 💻 命令行界面 (CLI)")
    print("      - 传统命令行批处理")
    print("      - 适合脚本化和自动化场景")
    print()
    print("🔧 系统工具:")
    print("   3. 🧪 运行完整检测")
    print("      - 整合所有检测功能")
    print("      - 项目代码、环境、依赖全面检查")
    print()
    print("   4. 🧹 项目清理工具")
    print("      - 清理缓存文件和临时数据")
    print("      - 清理输出结果和历史记录")
    print()
    print("📖 帮助信息:")
    print("   5. 📋 查看项目状态")
    print("      - 显示系统配置信息")
    print("      - 检查API密钥状态")
    print()
    print("   6. 📚 显示使用帮助")
    print("      - 查看详细使用说明")
    print("      - 常见问题解答")
    print()
    print("   7. ❌ 退出程序")
    print()
    print("-" * 50)


def run_web():
    """启动Web应用"""
    print("🚀 启动Web管理系统...")
    try:
        subprocess.run([sys.executable, "run_web.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Web应用启动失败: {e}")
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")


def run_cli():
    """启动CLI应用"""
    print("🚀 启动命令行界面...")
    try:
        subprocess.run([sys.executable, "run_cli.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ CLI应用启动失败: {e}")
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")


def run_tests():
    """运行测试"""
    print("🧪 启动完整系统检测...")
    try:
        subprocess.run([sys.executable, "check_all.py"], check=False)
    except Exception as e:
        print(f"❌ 检测运行失败: {e}")
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")


def run_cleanup():
    """运行清理工具"""
    print("🧹 启动项目清理工具...")
    try:
        subprocess.run([sys.executable, "tests/cleanup.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 清理工具运行失败: {e}")
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")


def show_project_status():
    """显示项目状态"""
    print("📋 项目状态检查...")
    try:
        # 导入配置服务检查状态
        sys.path.insert(0, str(Path(__file__).parent))
        from web.services.config_service import ConfigService

        config_service = ConfigService()
        status = config_service.get_system_status()

        print("\n" + "=" * 50)
        print("📊 系统状态报告")
        print("=" * 50)

        # API密钥状态
        print("🔑 API密钥状态:")
        api_keys = status.get("api_keys", {})
        for name, info in api_keys.items():
            status_icon = "✅" if info.get("configured") else "❌"
            env_key = info.get("env_key", "")
            print(f"   {status_icon} {name} ({env_key})")

        # 统计信息
        stats = status.get("statistics", {})
        print(f"\n📊 统计信息:")
        print(f"   🏢 云平台数量: {stats.get('providers', 0)}")
        print(f"   🤖 可用模型: {stats.get('models', 0)}")
        print(f"   📝 提示词模板: {stats.get('prompts', 0)}")

        # 目录状态
        print(f"\n📁 目录状态:")
        directories = status.get("directories", {})
        for name, info in directories.items():
            status_icon = "✅" if info.get("exists") else "❌"
            print(f"   {status_icon} {name}")

        # 配置文件状态
        print(f"\n📄 配置文件:")
        config_files = status.get("config_files", {})
        for name, exists in config_files.items():
            status_icon = "✅" if exists else "❌"
            print(f"   {status_icon} {name}")

        print("=" * 50)

    except Exception as e:
        print(f"❌ 状态检查失败: {e}")


def show_help():
    """显示帮助信息"""
    print("\n" + "=" * 60)
    print("📚 使用帮助")
    print("=" * 60)
    print("🚀 快速开始:")
    print("   1. 运行环境检测: python check_all.py")
    print("   2. 配置API密钥 (设置环境变量)")
    print("   3. 选择启动方式 (Web界面或CLI)")
    print("   4. 上传图片进行处理")
    print()
    print("🔍 环境检测:")
    print("   python check_all.py          # 统一检测入口（推荐）")
    print("   python tests/check_local.py  # 本地环境检测")
    print("   python tests/check_cloud.py  # 云服务器检测")
    print()
    print("🔑 API密钥配置:")
    print("   Windows CMD:")
    print("     set DASHSCOPE_API_KEY=your_key")
    print("     set ARK_API_KEY=your_key")
    print("   Windows PowerShell:")
    print("     $env:DASHSCOPE_API_KEY=\"your_key\"")
    print("   Linux/macOS:")
    print("     export DASHSCOPE_API_KEY=\"your_key\"")
    print()
    print("🌐 Web界面功能:")
    print("   • 📊 仪表板 - 系统状态概览")
    print("   • 🎯 任务处理 - 批量图片处理")
    print("   • 🤖 模型管理 - 云平台和模型配置")
    print("   • 📝 提示词库 - 提示词模板管理")
    print("   • 📋 任务历史 - 处理记录查看")
    print("   • ⚙️ 系统设置 - 配置管理")
    print()
    print("💻 CLI界面功能:")
    print("   • 交互式模型选择")
    print("   • 批量图片处理")
    print("   • 自定义参数配置")
    print("   • 处理结果查看")
    print()
    print("❓ 常见问题:")
    print("   Q: 环境配置问题?")
    print("   A: 运行 python check_all.py 进行全面检测")
    print()
    print("   Q: API密钥配置问题?")
    print("   A: 通过Web界面'系统设置'检查密钥状态")
    print()
    print("   Q: 模型连接测试失败?")
    print("   A: 使用Web界面'模型管理'进行连接测试")
    print()
    print("   Q: 如何优化处理性能?")
    print("   A: 调整max_workers参数，启用图片压缩")
    print("=" * 60)


def main():
    """主函数"""
    # 检查必要文件是否存在
    required_files = ["run_web.py", "run_cli.py", "tests/cleanup.py"]
    missing_files = [f for f in required_files if not Path(f).exists()]

    if missing_files:
        print("❌ 缺少必要文件:")
        for f in missing_files:
            print(f"   - {f}")
        print("\n请确保项目文件完整。")
        return 1

    # 显示项目信息
    show_project_info()

    while True:
        show_main_menu()

        try:
            choice = input("请输入选项 (1-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 感谢使用多模态批处理系统！")
            return 0

        if choice == "1":
            run_web()
        elif choice == "2":
            run_cli()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            run_cleanup()
        elif choice == "5":
            show_project_status()
        elif choice == "6":
            show_help()
        elif choice == "7":
            print("👋 感谢使用多模态批处理系统！")
            return 0
        else:
            print("❌ 无效选项，请重新选择。")

        # 询问是否继续
        print("\n" + "-" * 50)
        try:
            continue_choice = input("按回车键返回主菜单，或输入 'q' 退出: ").strip().lower()
            if continue_choice in ('q', 'quit', 'exit'):
                print("👋 感谢使用多模态批处理系统！")
                return 0
        except (EOFError, KeyboardInterrupt):
            print("\n👋 感谢使用多模态批处理系统！")
            return 0


if __name__ == "__main__":
    sys.exit(main())
