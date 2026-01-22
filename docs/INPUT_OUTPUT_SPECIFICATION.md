# 多模态批处理系统 - 输入输出规范

## 概述

本文档描述了多模态图片批处理系统的输入输出设计规范，供其他项目参考实现。

---

## 1. 项目目录结构

```
project_root/
├── config/                     # 配置文件目录
│   ├── models.yml              # 模型配置（必需）
│   ├── prompts/                # 提示词模板目录
│   │   └── default.yml         # 默认提示词
│   └── last_choice.json        # 上次选择记录（自动生成）
│
├── data/                       # 数据目录
│   ├── inputs/                 # 输入目录（放置待处理图片）
│   │   └── _web_uploads/       # Web上传临时目录（自动管理）
│   └── outputs/                # 输出目录（按模型名分组）
│       └── {Model-Name}/       # 每个模型一个子目录
│           ├── {图片名}_结果.json
│           └── run_summary.json
│
├── src/                        # 源代码目录
│   ├── config.py               # 默认配置常量
│   ├── config_loader.py        # 配置加载器
│   ├── processor.py            # 处理管线（统一入口）
│   ├── cli.py                  # 命令行接口
│   └── local/                  # 云API调用处理模块
│
├── .env                        # 环境变量（API密钥等）
├── run_cli.py                  # CLI启动脚本
└── run_web.py                  # Web启动脚本
```

---

## 2. 输入规范

### 2.1 输入目录
- **路径**: `data/inputs/`
- **支持格式**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- **命名规则**: 任意文件名，建议使用有意义的名称（如 `保修说明.png`）

### 2.2 输入处理流程
```
data/inputs/
    ├── image1.png      ──┐
    ├── image2.jpg      ──┼──> 批量处理 ──> data/outputs/{Model-Name}/
    └── image3.webp     ──┘
```

---

## 3. 输出规范

### 3.1 输出目录结构
```
data/outputs/
└── {Model-Name}/                    # 模型名（斜杠替换为连字符）
    ├── {图片名}_结果.json            # 单张图片结果
    ├── {图片名}_结果_1.json          # 重复处理时自动编号
    ├── {图片名}_结果_2.json
    └── run_summary.json             # 本次运行摘要
```

### 3.2 模型目录命名规则
| 原始模型名 | 目录名 |
|-----------|--------|
| `Qwen/Qwen2.5-VL-72B-Instruct` | `Qwen-Qwen2.5-VL-72B-Instruct` |
| `qwen-vl-plus` | `qwen-vl-plus` |

**规则**: 将 `/` 替换为 `-`

### 3.3 结果文件命名规则
| 输入文件 | 输出文件 |
|---------|---------|
| `保修说明.png` | `保修说明_结果.json` |
| `image.jpg` | `image_结果.json` |

**重复处理时**: `{图片名}_结果_1.json`, `{图片名}_结果_2.json`, ...

---

## 4. 输出JSON格式

### 4.1 单张图片结果 (`{图片名}_结果.json`)

```json
{
  "image_name": "保修说明.png",
  "processed_at": "2025-12-19 16:39:58",
  "model_name": "Qwen/Qwen2.5-VL-72B-Instruct",
  "context": {
    "image_path": "/path/to/image.png",
    "model_info": "模型描述信息"
  },
  "status": "success",
  "result": {
    // 模型输出的结构化内容（由prompt决定）
  }
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `image_name` | string | 原始图片文件名 |
| `processed_at` | string | 处理时间 (YYYY-MM-DD HH:MM:SS) |
| `model_name` | string | 使用的模型名称 |
| `context.image_path` | string | 图片完整路径 |
| `context.model_info` | string | 模型描述 |
| `status` | string | `"success"` 或 `"failed"` |
| `result` | object | 模型输出的结构化结果 |

### 4.2 运行摘要 (`run_summary.json`)

```json
{
  "model_name": "Qwen/Qwen2.5-VL-72B-Instruct",
  "model_info": "模型描述",
  "prompt": "使用的提示词...",
  "run_started_at": "2026-01-03 14:31:13",
  "run_finished_at": "2026-01-03 14:31:53",
  "elapsed_seconds": 39.65,
  "avg_seconds_per_image": 39.65,
  "max_workers": 2,
  "request_delay": 0.0,
  "max_retries": 2,
  "retry_delay": 5,
  "enable_compression": true,
  "max_image_size": [1024, 1024],
  "max_file_size_mb": 1,
  "input_dir": "/path/to/inputs",
  "output_dir": "/path/to/outputs",
  "totals": {
    "success": 10,
    "failed": 2,
    "all": 12
  },
  "images": [
    {
      "index": 1,
      "image_name": "image1.png",
      "status": "success",
      "output_file": "/path/to/output.json",
      "retries": 0,
      "timings": {
        "preprocess_seconds": 0.1,
        "api_seconds": 5.2,
        "parse_seconds": 0.01,
        "save_seconds": 0.01
      }
    }
  ]
}
```

---

## 5. 配置文件规范

### 5.1 模型配置 (`config/models.yml`)

```yaml
default_model:
  provider: "modelscope"
  model: "qwen2.5-vl-72b-instruct"

providers:
  cloud_provider:                     # 云API提供商
    key: aliyun
    display_name: "阿里云"
    defaults:
      api_base_url: "https://api.example.com/v1"
      env_key: "API_KEY_ENV_NAME"
    
    models:
      model-name:
        name: "model-api-name"
        label: "显示名称"
        info: "模型介绍"
```

### 5.2 提示词配置 (`config/prompts/default.yml`)

```yaml
name: "默认信息抽取"
description: "描述"
category: "分类"
tags: ["标签1", "标签2"]
is_default: true
prompt: |
  你是一名专业的信息抽取助手...
  输出要求：
  1. 仅输出合法 JSON
  2. ...
```

### 5.3 环境变量 (`.env`)

```bash
# 云API密钥
DASHSCOPE_API_KEY=sk-xxx
ARK_API_KEY=xxx
MODELSCOPE_ACCESS_TOKEN=xxx
HUNYUAN_API_KEY=xxx
```

---

## 6. 命名规范总结

| 类型 | 规范 | 示例 |
|------|------|------|
| 提供商key | 小写字母+下划线 | `local`, `aliyun`, `local_api` |
| 模型key | 小写字母+数字+连字符 | `qwen2.5-vl-7b-direct` |
| 模型name | 原始模型名 | `Qwen/Qwen2.5-VL-7B-Instruct` |
| 输出目录 | 模型name中`/`替换为`-` | `Qwen-Qwen2.5-VL-7B-Instruct` |
| 结果文件 | `{原文件名}_结果.json` | `保修说明_结果.json` |
| 摘要文件 | 固定名称 | `run_summary.json` |

---

## 7. 数据流图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户输入                                 │
├─────────────────────────────────────────────────────────────────┤
│  data/inputs/                                                    │
│    ├── image1.png                                               │
│    ├── image2.jpg                                               │
│    └── ...                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       处理管线 (Processor)                       │
├─────────────────────────────────────────────────────────────────┤
│  1. 读取 config/models.yml 获取模型配置                          │
│  2. 读取 config/prompts/default.yml 获取提示词                   │
│  3. 扫描 data/inputs/ 获取图片列表                               │
│  4. 调用云API处理图片                                            │
│  5. 批量处理图片，生成结构化JSON                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         输出结果                                 │
├─────────────────────────────────────────────────────────────────┤
│  data/outputs/{Model-Name}/                                      │
│    ├── image1_结果.json      # 单张图片结果                      │
│    ├── image2_结果.json                                          │
│    └── run_summary.json      # 运行摘要                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. 快速接入指南

### 8.1 最小实现要求

1. **输入**: 支持从 `data/inputs/` 读取图片
2. **输出**: 按模型名创建子目录，生成 `{图片名}_结果.json`
3. **配置**: 支持 `config/models.yml` 配置模型
4. **环境变量**: 支持 `.env` 文件读取API密钥

### 8.2 推荐实现

1. 支持多种模型类型（本地/云API）
2. 支持批量处理和并发
3. 生成 `run_summary.json` 统计信息
4. 支持重试机制
5. 支持图片压缩和尺寸限制

---

## 9. 示例代码结构

```python
# processor.py 核心接口
def run_pipeline(
    provider_key: str,          # 提供商key
    model_key: str,             # 模型key
    input_dir: str,             # 输入目录
    prompt: str,                # 提示词
    max_retries: int = 3,       # 最大重试次数
    ...
) -> None:
    """统一处理入口"""
    pass

# 输出结果格式
result = {
    "image_name": "xxx.png",
    "processed_at": "2026-01-03 12:00:00",
    "model_name": "model-name",
    "status": "success",
    "result": { ... }  # 模型输出
}
```

---

## 10. 注意事项

1. **编码**: 所有文件使用 UTF-8 编码
2. **路径**: 支持中文路径和文件名
3. **时间格式**: `YYYY-MM-DD HH:MM:SS`
4. **JSON**: 使用 `ensure_ascii=False` 保留中文
5. **错误处理**: 失败时 `status: "failed"`，`result` 包含错误信息
