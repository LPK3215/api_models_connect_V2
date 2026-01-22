# 🤝 贡献指南

感谢你对多模态批处理系统项目的关注！

## 🚀 快速开始

### 开发环境设置

1. **克隆项目**

```bash
git clone <repository-url>
cd multimodal-batch-processor
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置API密钥**

```bash
# 设置你需要的云平台API密钥
export DASHSCOPE_API_KEY="your_key"
export ARK_API_KEY="your_key"
# ... 其他密钥
```

4. **运行测试**

```bash
# 推荐：自动检测（快速）
python check_auto.py

# 或交互式检测
python check_interactive.py

# 或运行测试套件
python tests/test_all.py
```

## 🛠️ 开发流程

### 项目结构

```
├── check_auto.py           # 自动检测（推荐）
├── check_interactive.py    # 交互式检测
├── main.py                 # 应用启动器
├── run_web.py              # Web应用启动入口
├── run_cli.py              # CLI应用启动入口
├── src/                # 核心代码
├── web/                # Web应用
├── tests/              # 测试和检测工具
│   ├── check_project.py  # 项目代码检测
│   ├── check_local.py    # 本地环境检测
│   ├── check_cloud.py    # 云服务器检测
│   ├── test_all.py       # 完整测试套件
│   └── cleanup.py        # 清理工具
└── config/             # 配置文件
```

### 代码规范

- 遵循 PEP 8 编码规范
- 使用 flake8 检查代码质量
- 为函数添加类型注解和文档注释
- 保持代码简洁和可读性

### 提交代码

1. **创建功能分支**

```bash
git checkout -b feature/your-feature-name
```

2. **编写代码和测试**
    - 为新功能编写测试
    - 运行完整测试套件确保通过
    - 遵循项目代码规范

3. **提交更改**

```bash
git add .
git commit -m "feat: 添加新功能描述"
```

4. **推送并创建 PR**

```bash
git push origin feature/your-feature-name
```

## 📝 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

## 🧪 测试

### 运行完整检测（推荐）

```bash
# 自动检测（快速）
python check_auto.py

# 交互式检测（可选择项目）
python check_interactive.py
# 选择 5 - 全面检测
```

### 运行测试套件

```bash
python tests/test_all.py
```

### 测试内容

- 配置文件加载测试
- API密钥验证测试
- 模型连接测试
- 提示词管理测试
- 系统状态检查
- Web功能验证

### 编写测试

- 在 `tests/test_all.py` 中添加新的测试方法
- 确保测试覆盖新功能
- 测试应该独立且可重复运行

## 📚 添加新云平台

1. **更新模型配置**
    - 在 `config/models.yml` 中添加新平台配置
    - 包含平台信息、API配置和模型列表

2. **测试配置**
    - 在 `tests/test_all.py` 中添加相应测试
    - 确保配置加载和模型连接正常

3. **更新文档**
    - 更新 README.md 中的支持平台列表
    - 添加API密钥配置说明

## 🌐 扩展Web功能

1. **修改Web应用**
    - 主要代码在 `web/app.py`
    - 服务层代码在 `web/services/`

2. **测试Web功能**
    - 在 `tests/test_all.py` 中添加Web功能测试
    - 确保新功能正常工作

## 💻 扩展CLI功能

1. **修改CLI代码**
    - 主要代码在 `src/cli.py`
    - 处理逻辑在 `src/processor.py`

2. **测试CLI功能**
    - 通过 `run_cli.py` 测试新功能
    - 确保命令行参数正确处理

## 🧹 项目维护

### 清理工具

```bash
python tests/cleanup.py
```

### 系统检测

```bash
# 推荐：自动检测（快速）
python check_auto.py

# 或交互式检测
python check_interactive.py

# 或单独检测
python tests/check_project.py  # 项目代码
python tests/check_local.py    # 本地环境
python tests/check_cloud.py    # 云服务器
```

## 🐛 报告问题

请使用 GitHub Issues 报告问题，包含：

- 问题描述和复现步骤
- 期望行为 vs 实际行为
- 环境信息（Python版本、操作系统等）
- 相关的错误日志

## 💡 功能建议

欢迎提出新功能建议！请先创建 Issue 讨论：

- 功能描述和使用场景
- 实现思路和技术方案
- 对现有功能的影响

## 📄 许可证

通过贡献代码，你同意你的贡献将在 MIT 许可证下发布。

---

**感谢你的贡献！让我们一起让这个项目变得更好！** 🎉