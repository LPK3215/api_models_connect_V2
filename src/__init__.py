"""
多模态批处理系统 - 源代码包

目录结构:
- local/: 本地开发机模块（调用云平台API）
- cloud/: 云服务器模块（调用本地部署的模型）
- config.py: 全局配置
- config_loader.py: 配置加载器
- processor.py: 统一处理入口
- cli.py: 命令行接口

环境检测相关模块在 tests/checkers/ 目录
"""

__version__ = "1.0.0"
__author__ = "Multi-Modal Batch Processor Team"
__description__ = "多模态批处理系统 - 支持云API和本地模型的图片批处理工具"
__license__ = "MIT"

# 导出版本信息
__all__ = ["__version__", "__author__", "__description__", "__license__"]
