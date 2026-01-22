# 🚀 多模态批处理系统

一个现代化的多云平台图片批处理工具，通过云API调用大模型处理图片。

## ✨ 功能特点

- 🤖 **多云平台支持**：阿里云DashScope、豆包/火山方舟、魔塔ModelScope、腾讯混元
- 🖼️ **批量图片处理**：支持多张图片同时处理，自动压缩优化
- 📝 **结构化信息抽取**：从图片中提取JSON格式数据
- 🌐 **前后端分离**：后端 FastAPI + 前端 Vue
- 💻 **CLI**：保留命令行入口，便于脚本化运行
- 🔧 **环境检测工具**：自动检测环境配置，给出修复建议

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r backend/requirements.txt
```

### 2. 配置 API 密钥

```bash
# Windows CMD
set DASHSCOPE_API_KEY=your_key

# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_key"

# Linux/macOS
export DASHSCOPE_API_KEY=your_key
```

或在 `.env` 文件中配置：
```
DASHSCOPE_API_KEY=your_key
ARK_API_KEY=your_key
MODELSCOPE_ACCESS_TOKEN=your_key
HUNYUAN_API_KEY=your_key
```

### 3. 环境检测

```bash
# 自动检测（推荐）
cd backend
python scripts/check_auto.py

# 交互式检测
python scripts/check_interactive.py

# 项目健康检查
python tests/check_project.py
```

### 4. 启动

```bash
# 1) 启动后端 API (FastAPI)
cd backend
python run_api.py

# 2) 启动前端 (Vue)
cd ..\\frontend
npm install
npm run dev

# (可选) CLI
cd ..\\backend
python run_cli.py --select
```

- 前端: http://127.0.0.1:5173
- 后端 OpenAPI: http://127.0.0.1:8000/docs

## 📁 项目结构

```
├── frontend/                  # 前端 (Vue)
├── backend/                   # 后端 (FastAPI + 核心处理逻辑)
│   ├── run_api.py             # 后端 API 入口
│   ├── run_cli.py             # CLI 入口
│   ├── src/backend/           # 后端源码包
│   ├── scripts/               # 检测脚本
│   ├── tests/                 # 测试和检测工具
│   ├── config/                # 模型配置、提示词库
│   └── data/                  # 输入/输出数据
└── docs/                      # 文档
```

## 🤖 支持的云平台

| 平台            | 模型                        | 环境变量                      |
|---------------|---------------------------|---------------------------|
| 阿里云 DashScope | qwen-vl-plus, qwen-vl-max | `DASHSCOPE_API_KEY`       |
| 豆包/火山方舟       | doubao-vision             | `ARK_API_KEY`             |
| 魔塔 ModelScope | Qwen2.5-VL-72B 等          | `MODELSCOPE_ACCESS_TOKEN` |
| 腾讯混元          | hunyuan-vision            | `HUNYUAN_API_KEY`         |

## 🔧 常用命令

```bash
# 环境检测
cd backend
python scripts/check_auto.py
python tests/check_project.py

# 后端 + 前端
python run_api.py             # FastAPI 后端
cd ..\\frontend; npm run dev  # Vue 前端

# (可选) CLI
cd ..\\backend
python run_cli.py --select

# 测试
cd backend
python tests/test_all.py
python tests/quick_check.py
```

## 📖 文档

- [完整文档](docs/README.md)
- [输入输出规范](docs/INPUT_OUTPUT_SPECIFICATION.md)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)
