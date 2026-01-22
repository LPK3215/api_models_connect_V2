# 🚀 多模态批处理系统

一个现代化的多云平台图片批处理工具，通过云API调用大模型处理图片。

## ✨ 功能特点

- 🤖 **多云平台支持**：阿里云DashScope、豆包/火山方舟、魔塔ModelScope、腾讯混元
- 🖼️ **批量图片处理**：支持多张图片同时处理，自动压缩优化
- 📝 **结构化信息抽取**：从图片中提取JSON格式数据
- 🌐 **Web界面 + CLI**：两种使用方式，灵活选择
- 🔧 **环境检测工具**：自动检测环境配置，给出修复建议

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
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
python check_auto.py

# 交互式检测
python check_interactive.py

# 项目健康检查
python tests/check_project.py
```

### 4. 启动

```bash
# 启动器（推荐）
python main.py

# 或直接启动
python run_web.py      # Web 界面
python run_cli.py --select  # 命令行（交互选择模型）
```

## 📁 项目结构

```
├── check_auto.py           # 自动检测（推荐）
├── check_interactive.py    # 交互式检测
├── main.py                 # 应用启动器
├── run_cli.py              # CLI 运行入口
├── run_web.py              # Web 界面入口
├── config/
│   ├── models.yml          # 模型配置
│   └── prompts/            # 提示词模板
├── data/
│   ├── inputs/             # 输入图片
│   └── outputs/            # 输出结果
├── src/                    # 核心代码
├── tests/                  # 测试和检测工具
├── web/                    # Web 界面
└── docs/                   # 文档
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
python check_auto.py          # 自动检测
python tests/check_project.py # 项目健康检查

# 运行
python run_cli.py --select    # CLI交互选择模型
python run_web.py             # Web界面

# 测试
python tests/test_all.py      # 运行测试
python tests/quick_check.py   # 快速检查
```

## 📖 文档

- [完整文档](docs/README.md)
- [输入输出规范](docs/INPUT_OUTPUT_SPECIFICATION.md)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)
