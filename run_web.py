#!/usr/bin/env python3
"""
Web应用运行入口
启动Web管理系统
"""

import os
import random
import socket
import sys
import warnings
from pathlib import Path

# 过滤 Gradio 6.0 的 CSS 参数警告（已知问题，不影响功能）
warnings.filterwarnings("ignore", message=".*parameters have been moved.*Blocks constructor.*")

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 让 Gradio 的上传临时目录落在项目盘符下，避免跨盘复制导致 Web 处理变慢
try:
    gradio_tmp = project_root / "data" / "inputs" / "_web_uploads" / "_gradio_tmp"
    gradio_tmp.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("GRADIO_TEMP_DIR", str(gradio_tmp))
except Exception:
    pass

from web.app import create_web_app

# 端口池配置
PORT_POOL = [8081, 8082, 8083, 8084, 8085, 7860, 7861, 7862, 7863]


def is_port_available(port):
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            return result != 0
    except Exception:
        return False


def get_available_port():
    """从端口池中获取可用端口"""
    # 随机打乱端口池
    available_ports = PORT_POOL.copy()
    random.shuffle(available_ports)

    for port in available_ports:
        if is_port_available(port):
            return port

    # 如果端口池都被占用，尝试系统自动分配
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('127.0.0.1', 0))
            return sock.getsockname()[1]
    except Exception:
        return None


def main():
    """启动Web管理系统"""
    print("🚀 启动多模态批处理 Web 管理系统...")

    try:
        # 获取可用端口
        port = get_available_port()
        if port is None:
            print("❌ 无法找到可用端口")
            sys.exit(1)

        print(f"🔍 检测到可用端口: {port}")

        app = create_web_app()
        print("📱 Web应用已创建，正在启动服务器...")

        # 启动服务器
        app.launch(
            server_name="127.0.0.1",
            server_port=port,
            share=False,
            show_error=True,
        )

    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 提示：请检查网络连接或尝试重新启动")
        sys.exit(1)


if __name__ == "__main__":
    main()
