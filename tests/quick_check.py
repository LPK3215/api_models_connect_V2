#!/usr/bin/env python3
"""
快速启动前检查脚本
在运行云API调用前，快速验证环境是否就绪
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_api_keys():
    """检查 API 密钥是否配置"""
    import os
    
    api_keys = {
        "DASHSCOPE_API_KEY": "阿里云 DashScope",
        "ARK_API_KEY": "豆包/火山方舟",
        "MODELSCOPE_ACCESS_TOKEN": "魔塔 ModelScope",
        "HUNYUAN_API_KEY": "腾讯混元",
    }
    
    configured = []
    missing = []
    
    for key, name in api_keys.items():
        if os.environ.get(key):
            configured.append((key, name))
        else:
            missing.append((key, name))
    
    if configured:
        return True, f"✅ 已配置 {len(configured)} 个API密钥: {', '.join([n for _, n in configured])}"
    else:
        return False, "❌ 未配置任何API密钥"


def check_dependencies():
    """检查关键依赖"""
    deps = {
        "yaml": "PyYAML (配置文件)",
        "requests": "Requests (HTTP请求)",
        "PIL": "Pillow (图片处理)",
        "openai": "OpenAI (API客户端)",
    }

    results = []
    for module, name in deps.items():
        try:
            __import__(module)
            results.append((True, f"✅ {name}"))
        except ImportError:
            results.append((False, f"❌ {name}"))

    return results


def check_config():
    """检查配置文件"""
    try:
        from src.config_loader import get_providers
        providers = get_providers()
        return True, f"✅ 配置加载成功 ({len(providers)} 个云平台)"
    except Exception as e:
        return False, f"❌ 配置加载失败: {e}"


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 云API调用环境快速检查")
    print("=" * 70)
    print()

    all_passed = True

    # 1. 依赖检查
    print("📌 1. 关键依赖检查")
    dep_results = check_dependencies()
    for ok, msg in dep_results:
        print(f"   {msg}")
        if not ok:
            all_passed = False
    if not all([ok for ok, _ in dep_results]):
        print("   💡 修复: pip install -r requirements.txt")
    print()

    # 2. 配置检查
    print("📌 2. 配置文件检查")
    config_ok, config_msg = check_config()
    print(f"   {config_msg}")
    if not config_ok:
        all_passed = False
    print()

    # 3. API密钥检查
    print("📌 3. API密钥检查")
    api_ok, api_msg = check_api_keys()
    print(f"   {api_msg}")
    if not api_ok:
        all_passed = False
        print("   💡 修复: 在 .env 文件或环境变量中配置API密钥")
    print()

    # 总结
    print("=" * 70)
    if all_passed:
        print("✅ 所有检查通过！可以开始使用云API")
        print()
        print("🚀 启动命令:")
        print("   CLI模式: python run_cli.py --select")
        print("   Web模式: python run_web.py")
    else:
        print("⚠️  部分检查未通过，请先修复上述问题")
        print()
        print("💡 完整环境检测:")
        print("   python tests/check_cloud.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
