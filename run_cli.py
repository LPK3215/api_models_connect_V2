#!/usr/bin/env python3
"""
本地CLI运行入口
启动命令行批处理界面
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.cli import main as cli_main


def main():
    """启动CLI界面"""
    print("🚀 启动多模态批处理 CLI 界面...")

    # 获取命令行参数（跳过脚本名）
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--select"]

    try:
        cli_main(args)
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
