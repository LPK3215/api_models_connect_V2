# 📚 文档索引

## 概述

本项目是一个多云平台图片批处理工具，通过云 API 调用多模态大模型处理图片，支持阿里云、豆包/火山方舟、魔塔 ModelScope、腾讯混元等平台。

## 文档列表

| 文档                                                 | 说明         |
|----------------------------------------------------|------------|
| [INPUT_OUTPUT_SPECIFICATION.md](./INPUT_OUTPUT_SPECIFICATION.md) | 输入输出规范 |
| [PROJECT_STATUS.md](./PROJECT_STATUS.md)           | 项目状态     |
| [CONTRIBUTING.md](./CONTRIBUTING.md)               | 贡献指南     |

---

## 快速开始

### 本地开发环境

1. 安装后端依赖：`pip install -r backend/requirements.txt`
2. 配置 API 密钥（在 repo 根目录 `.env` 或系统环境变量中）
3. 后端环境检测：
   - `cd backend; python scripts/check_auto.py`
4. 启动后端 + 前端：
   - 后端：`cd backend; python run_api.py`
   - 前端：`cd frontend; npm install; npm run dev`

### 支持的云平台

- **阿里云 DashScope**: 通义千问系列模型
- **豆包/火山方舟**: 豆包视觉模型
- **魔塔 ModelScope**: Qwen2.5-VL 等模型
- **腾讯混元**: 混元视觉模型

---

## 项目结构

```
├── backend/                # 后端 (FastAPI + 核心处理逻辑)
│   ├── run_api.py          # FastAPI 入口
│   ├── run_cli.py          # CLI 入口
│   ├── src/backend/        # 后端源码包
│   ├── config/             # models.yml + prompts/*.yml
│   ├── scripts/            # 环境检测脚本
│   ├── tests/              # 测试与检查
│   └── data/               # 输入/输出目录
├── frontend/               # 前端 (Vue3 + TS + Tailwind)
└── docs/                   # 文档
```

---

## 常用命令

```bash
# 环境检测
cd backend
python scripts/check_auto.py
python tests/check_project.py

# 启动
python run_api.py           # FastAPI 后端
cd ..\frontend; npm run dev  # Vue 前端
cd ..\backend; python run_cli.py --select  # (可选) CLI

# 测试
cd backend
pytest -q
```
