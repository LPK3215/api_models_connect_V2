# 📚 文档索引

## 概述

本项目是一个多云平台图片批处理工具，通过云API调用大模型处理图片，支持阿里云、豆包、魔塔、腾讯混元等平台。

## 文档列表

| 文档                                                 | 说明         |
|----------------------------------------------------|------------|
| [INPUT_OUTPUT_SPECIFICATION.md](./INPUT_OUTPUT_SPECIFICATION.md) | 输入输出规范 |
| [PROJECT_STATUS.md](./PROJECT_STATUS.md)           | 项目状态     |
| [CONTRIBUTING.md](./CONTRIBUTING.md)               | 贡献指南     |

---

## 快速开始

### 本地开发环境

1. 安装依赖：`pip install -r requirements.txt`
2. 配置API密钥（在 `.env` 文件或环境变量中）
3. 运行检测：`python check_auto.py`
4. 启动应用：`python main.py`

### 支持的云平台

- **阿里云 DashScope**: 通义千问系列模型
- **豆包/火山方舟**: 豆包视觉模型
- **魔塔 ModelScope**: Qwen2.5-VL 等模型
- **腾讯混元**: 混元视觉模型

---

## 项目结构

```
├── src/                    # 核心代码
│   ├── config.py           # 配置常量
│   ├── config_loader.py    # 配置加载器
│   ├── processor.py        # 处理管线
│   ├── cli.py              # 命令行接口
│   └── local/              # 云API处理模块
├── web/                    # Web界面
├── tests/                  # 测试和检测工具
├── config/                 # 配置文件
└── data/                   # 数据目录
```

---

## 常用命令

```bash
# 环境检测
python check_auto.py
python tests/check_project.py

# 运行应用
python main.py              # 启动器
python run_cli.py --select  # CLI
python run_web.py           # Web

# 测试
python tests/test_all.py
```
