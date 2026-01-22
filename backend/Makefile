# 多模态批处理系统 - 项目管理 Makefile

.PHONY: help install test lint format clean run-cli run-api cleanup check

help:  ## 显示帮助信息
	@echo "🚀 多模态批处理系统 - 可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 安装项目依赖
	@echo "📦 安装项目依赖..."
	pip install -r requirements.txt
	@echo "✅ 依赖安装完成！"

check:  ## 运行完整系统检测（推荐）
	@echo "🔍 运行完整系统检测..."
	python scripts/check_auto.py

check-project:  ## 检测项目代码
	@echo "🏗️  检测项目代码..."
	python tests/check_project.py

check-local:  ## 检测本地环境
	@echo "💻 检测本地环境..."
	python tests/check_local.py

check-cloud:  ## 检测云服务器环境
	@echo "☁️  检测云服务器环境..."
	python tests/check_cloud.py

test:  ## 运行完整测试套件
	@echo "🧪 运行完整测试套件..."
	python tests/test_all.py

lint:  ## 代码质量检查
	@echo "🔍 代码质量检查..."
	flake8 src/backend/ tests/ --max-line-length=100

format:  ## 格式化代码（如果安装了black）
	@echo "🎨 格式化代码..."
	@if command -v black >/dev/null 2>&1; then \
		black src/backend/ tests/ --line-length=100; \
		echo "✅ 代码格式化完成！"; \
	else \
		echo "⚠️  black未安装，跳过格式化"; \
	fi

clean:  ## 清理项目文件
	@echo "🧹 启动项目清理工具..."
	python tests/cleanup.py

clean-cache:  ## 清理Python缓存文件
	@echo "🗂️  清理Python缓存文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ 缓存文件清理完成！"

run-api:  ## 启动后端 API (FastAPI)
	@echo "🌐 启动后端 API (FastAPI)..."
	python run_api.py

run-cli:  ## 直接启动CLI界面
	@echo "💻 启动CLI界面..."
	python run_cli.py

status:  ## 检查项目状态
	@echo "📊 检查项目状态..."
	@python -c "import sys; sys.path.insert(0, 'src'); from backend.services.config_service import ConfigService; cs = ConfigService(); status = cs.get_system_status(); print(f'云平台: {status[\"statistics\"][\"providers\"]}个, 模型: {status[\"statistics\"][\"models\"]}个, 提示词: {status[\"statistics\"][\"prompts\"]}个')"

check-deps:  ## 检查依赖是否安装
	@echo "🔍 检查依赖..."
	@python -c "import openai, yaml, PIL, fastapi, uvicorn, multipart; print('✅ 核心依赖已安装')" 2>/dev/null || echo "❌ 缺少依赖，请运行 make install"

dev-setup: install  ## 开发环境设置
	@echo "🛠️  开发环境设置完成！"
	@echo "📚 运行 'make help' 查看可用命令"
	@echo "🚀 运行 'make run-api' 启动后端"

quick-start: check-deps status run-api  ## 快速启动（检查+启动）
