"""
Web 管理应用
基于 Gradio 构建的完整管理系统
"""
from __future__ import annotations

import threading
import time
from datetime import datetime
from pathlib import Path

import gradio as gr

from src.processor import Processor
from web.services.config_service import ConfigService


class WebApp:
    """Web 应用主类"""

    def __init__(self):
        self._config_service = None
        self._processor = None

    @property
    def config_service(self):
        if self._config_service is None:
            self._config_service = ConfigService()
        return self._config_service

    @property
    def processor(self):
        if self._processor is None:
            self._processor = Processor()
        return self._processor

    def create_app(self) -> gr.Blocks:
        """创建主应用"""

        # 完整样式：防抖动 + 色彩 + 标签导航 + 按钮 + 标题 + 视觉优化
        custom_css = """
        /* === 防抖动核心 === */
        html, body {
            overflow-x: hidden !important;
            overflow-y: scroll !important;
        }
        
        .gradio-container {
            max-width: 100% !important;
            overflow-x: hidden !important;
            padding: 20px !important;
        }
        
        /* 标签页内容固定最小高度 + 宽松间距 */
        .tabitem {
            min-height: 550px !important;
            overflow-y: auto !important;
            padding: 25px 30px !important;
        }
        
        /* === 标签页导航样式 === */
        .tabs > .tab-nav,
        div[role="tablist"] {
            justify-content: center !important;
            background: linear-gradient(180deg, #f8f9fa 0%, #f0f1f3 100%) !important;
            border-bottom: 1px solid #e0e0e0 !important;
            padding: 14px 0 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03) !important;
        }
        
        /* 标签按钮 - 字体放大 + 优化过渡 */
        button[role="tab"] {
            margin: 0 8px !important;
            padding: 12px 24px !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            border: none !important;
            background: transparent !important;
            color: #555 !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: relative !important;
        }
        
        button[role="tab"]:hover {
            background: rgba(102, 126, 234, 0.1) !important;
            color: #667eea !important;
            transform: translateY(-1px) !important;
        }
        
        /* 选中的标签页 */
        button[aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        
        /* === 页面内标题居中 === */
        .markdown h3, .markdown h4,
        .gr-markdown h3, .gr-markdown h4 {
            text-align: center !important;
            color: #2d3748 !important;
            margin: 20px 0 !important;
        }
        
        /* === 按钮样式优化 === */
        button.primary, .gradio-button.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
            font-weight: 600 !important;
        }
        
        button.primary:hover, .gradio-button.primary:hover {
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
            transform: translateY(-2px) !important;
            filter: brightness(1.05) !important;
        }
        
        button.primary:active, .gradio-button.primary:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        }
        
        button.secondary, .gradio-button.secondary {
            background: linear-gradient(180deg, #ffffff 0%, #f5f5f5 100%) !important;
            color: #444 !important;
            border: 1px solid #ddd !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        }
        
        button.secondary:hover, .gradio-button.secondary:hover {
            background: linear-gradient(180deg, #ffffff 0%, #eeeeee 100%) !important;
            border-color: #ccc !important;
            box-shadow: 0 3px 10px rgba(0,0,0,0.12) !important;
            transform: translateY(-1px) !important;
        }
        
        button.stop, .gradio-button.stop {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
            border: none !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3) !important;
        }
        
        button.stop:hover, .gradio-button.stop:hover {
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5) !important;
            transform: translateY(-2px) !important;
            filter: brightness(1.05) !important;
        }
        
        /* === 组件间距 === */
        .gr-form, .gr-box {
            padding: 15px !important;
        }
        
        .gr-padded {
            padding: 16px !important;
        }
        
        /* Row 间距 */
        .gr-row, .row {
            margin-bottom: 12px !important;
        }
        
        /* JSON 显示区域 */
        .gradio-json {
            max-height: 300px !important;
            overflow: auto !important;
            border-radius: 8px !important;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        
        /* 滚动条美化 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #c0c0c0 0%, #a0a0a0 100%);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #a0a0a0 0%, #888888 100%);
        }
        
        /* 隐藏 Gradio 6.x 的进度时间显示 */
        .progress-text, .eta-text, .timer {
            display: none !important;
        }

        /* 隐藏进度条右侧的时间文本 */
        .progress-bar + span, .progress-level + span {
            display: none !important;
        }

        /* 更激进地隐藏 Gradio 内置进度区域 */
        .gradio-container [role="progressbar"],
        .gradio-container .progress,
        .gradio-container .progress-container,
        .gradio-container .progress-bar,
        .gradio-container [data-testid*="progress"],
        .gradio-container [class*="progress"] {
            display: none !important;
        }
        
        /* 稳定计时器显示区域，防止布局抖动 */
        .timer-display-area pre {
            min-height: 60px !important;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
            margin: 0 !important;
            white-space: pre !important;
            line-height: 1.5 !important;
        }
        
        /* 固定状态显示区域高度，防止内容变化时跳动 */
        .status-display-area {
            min-height: 100px !important;
        }
        
        /* === 下拉框优化 === */
        .gr-dropdown, select {
            transition: all 0.2s ease !important;
            border-radius: 8px !important;
        }
        
        .gr-dropdown:hover, select:hover {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        }
        
        .gr-dropdown:focus, select:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        }
        
        /* === 输入框优化 === */
        input[type="text"], textarea {
            transition: all 0.2s ease !important;
            border-radius: 8px !important;
        }
        
        input[type="text"]:hover, textarea:hover {
            border-color: #667eea !important;
        }
        
        input[type="text"]:focus, textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
            outline: none !important;
        }
        
        /* === 文件上传区域优化 === */
        .gr-file-upload, [data-testid="file"] {
            border: 2px dashed #d0d0d0 !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%) !important;
        }
        
        .gr-file-upload:hover, [data-testid="file"]:hover {
            border-color: #667eea !important;
            background: linear-gradient(180deg, #f8f9ff 0%, #f0f2ff 100%) !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15) !important;
        }
        
        /* === Accordion 折叠面板优化 === */
        .gr-accordion {
            border-radius: 10px !important;
            overflow: hidden !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        }
        
        .gr-accordion > button {
            transition: all 0.2s ease !important;
        }
        
        .gr-accordion > button:hover {
            background: #f8f9fa !important;
        }
        """

        # Gradio 6.0 警告可忽略，CSS 仍需在此传入
        with gr.Blocks(title="多模态批处理管理系统", css=custom_css) as app:
            # 应用头部 - 带样式
            gr.HTML("""
            <div style="text-align: center; padding: 28px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);">
                <h1 style="margin: 0; font-size: 32px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">🚀 多模态批处理管理系统</h1>
                <p style="margin: 12px 0 0 0; opacity: 0.95; font-size: 15px; font-weight: 400;">统一管理云平台模型，批量处理图片任务，提取结构化信息</p>
            </div>
            """)

            # 主标签页
            with gr.Tabs():
                # 1. 仪表板
                with gr.Tab("📊 仪表板"):
                    self._create_dashboard_tab()

                # 2. 任务处理
                with gr.Tab("🎯 任务处理"):
                    self._create_task_tab()

                # 3. 模型管理
                with gr.Tab("🤖 模型管理"):
                    self._create_model_tab()

                # 4. 提示词库
                with gr.Tab("📝 提示词库"):
                    self._create_prompt_tab()

                # 5. 任务历史
                with gr.Tab("📋 任务历史"):
                    self._create_history_tab()

                # 6. 系统设置
                with gr.Tab("⚙️ 系统设置"):
                    self._create_settings_tab()

            # 底部说明
            gr.HTML("""
            <div style="margin-top: 20px; padding: 16px 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 12px; border: 1px solid #dee2e6; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div style="color: #495057; font-size: 14px;">
                    <strong style="color: #667eea;">🚀 多模态批处理管理系统</strong>
                    <span style="margin: 0 8px; color: #dee2e6;">|</span>
                    <span style="color: #0d6efd;">多云平台AI模型统一管理</span>
                    <span style="margin: 0 8px; color: #dee2e6;">|</span>
                    <span style="color: #198754;">高效批量图片处理</span>
                    <span style="margin: 0 8px; color: #dee2e6;">|</span>
                    <span style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;">v1.0</span>
                </div>
                <div style="color: #6c757d; margin-top: 10px; font-size: 13px;">
                    💡 首次使用请先在「系统设置」中配置API密钥，然后在「模型管理」中测试连接状态
                </div>
            </div>
            """)

        return app

    def _create_dashboard_tab(self):
        """创建仪表板标签页"""

        def get_dashboard_stats():
            status = self.config_service.get_system_status()
            stats = status["statistics"]
            history_stats = self.config_service.get_history_statistics()

            return f"""
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px 20px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35); transition: all 0.3s ease;">
        <div style="font-size: 36px; margin-bottom: 8px;">🏢</div>
        <h3 style="margin: 0; font-size: 32px; font-weight: 700;">{stats['providers']}</h3>
        <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">云平台数量</p>
    </div>
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 24px 20px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(240, 147, 251, 0.35); transition: all 0.3s ease;">
        <div style="font-size: 36px; margin-bottom: 8px;">🤖</div>
        <h3 style="margin: 0; font-size: 32px; font-weight: 700;">{stats['models']}</h3>
        <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">可用模型</p>
    </div>
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 24px 20px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(79, 172, 254, 0.35); transition: all 0.3s ease;">
        <div style="font-size: 36px; margin-bottom: 8px;">📝</div>
        <h3 style="margin: 0; font-size: 32px; font-weight: 700;">{stats['prompts']}</h3>
        <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">提示词模板</p>
    </div>
    <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 24px 20px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(67, 233, 123, 0.35); transition: all 0.3s ease;">
        <div style="font-size: 36px; margin-bottom: 8px;">📊</div>
        <h3 style="margin: 0; font-size: 32px; font-weight: 700;">{history_stats['success_rate']:.0f}%</h3>
        <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">任务成功率</p>
    </div>
</div>
"""

        dashboard_display = gr.Markdown(get_dashboard_stats())

        def get_api_status():
            status = self.config_service.get_system_status()
            api_html = "<h3 style='text-align: center; color: #4a5568; margin-bottom: 16px;'>🔑 API 密钥状态</h3>"
            api_html += "<div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;'>"

            for name, info_data in status["api_keys"].items():
                if info_data["configured"]:
                    bg_color = "linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)"
                    border_color = "#28a745"
                    text_color = "#155724"
                else:
                    bg_color = "linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%)"
                    border_color = "#dc3545"
                    text_color = "#721c24"
                
                status_icon = "✅" if info_data["configured"] else "❌"
                status_text = "已配置" if info_data["configured"] else "未配置"

                api_html += f"""
                <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: all 0.3s ease;">
                    <div style="font-size: 24px; margin-bottom: 8px;">{status_icon}</div>
                    <div style="font-weight: 700; margin-bottom: 6px; color: #2d3748; font-size: 14px;">{name}</div>
                    <div style="color: {text_color}; font-size: 13px; font-weight: 600;">{status_text}</div>
                    <div style="color: #718096; font-size: 11px; margin-top: 8px; padding: 4px 8px; background: rgba(255,255,255,0.5); border-radius: 4px; font-family: monospace;">{info_data['env_key']}</div>
                </div>
                """

            api_html += "</div>"
            return api_html

        api_status_display = gr.Markdown(get_api_status())

        # 操作按钮
        with gr.Row():
            refresh_btn = gr.Button("🔄 刷新", variant="primary")
            test_all_btn = gr.Button("🧪 测试全部")
            clear_cache_btn = gr.Button("🧹 清理缓存")

        status_display = gr.Markdown("")

        def refresh_all():
            return get_dashboard_stats(), get_api_status(), "✅ 数据已刷新"

        def test_all_connections():
            try:
                providers = list(self.config_service.get_all_providers().keys())
                results = []

                for provider_key in providers:
                    models = self.config_service.get_models_by_provider(provider_key)
                    provider_name = self.config_service.get_provider_info(provider_key)['info']['display_name']

                    if models:
                        first_model = list(models.keys())[0]
                        test_result = self._test_single_connection(provider_key, first_model)
                        if "✅" in test_result:
                            results.append(f"✅ {provider_name}: 连接正常")
                        else:
                            results.append(f"❌ {provider_name}: 连接失败")
                    else:
                        results.append(f"⚠️ {provider_name}: 无可用模型")

                return "\n".join(results)
            except Exception as e:
                return f"❌ 批量测试失败: {str(e)}"

        def clear_system_cache():
            try:
                from src.local.api_client import _CLIENT_POOL
                from src.local.image_utils import _IMAGE_CACHE
                _IMAGE_CACHE.clear()
                _CLIENT_POOL.clear()

                from src.config_loader import refresh_providers
                refresh_providers()

                return "✅ 系统缓存已清理"
            except Exception as e:
                return f"❌ 清理失败: {str(e)}"

        refresh_btn.click(fn=refresh_all, outputs=[dashboard_display, api_status_display, status_display])
        test_all_btn.click(fn=test_all_connections, outputs=[status_display])
        clear_cache_btn.click(fn=clear_system_cache, outputs=[status_display])

    def _test_single_connection(self, provider_key: str, model_key: str) -> str:
        """测试单个模型连接"""
        try:
            from src.config_loader import get_provider, get_model
            import os

            provider = get_provider(provider_key)
            model_config = get_model(provider_key, model_key)

            provider_defaults = provider["info"].get("defaults", {})
            env_key = model_config.get("env_key") or provider_defaults.get("env_key")

            if not env_key:
                return f"❌ 未找到API密钥配置"

            api_key = os.getenv(env_key)
            if not api_key:
                return f"❌ API 密钥未配置 (环境变量: {env_key})"

            api_base_url = model_config.get("api_base_url") or provider_defaults.get("api_base_url")
            if not api_base_url:
                return f"❌ API Base URL 未配置"

            from openai import OpenAI
            import time

            client = OpenAI(api_key=api_key, base_url=api_base_url, timeout=10.0)
            test_messages = [{"role": "user", "content": "测试"}]

            start_time = time.time()
            try:
                completion = client.chat.completions.create(
                    model=model_config["name"],
                    messages=test_messages,
                    max_tokens=5
                )

                response_time = time.time() - start_time

                if completion.choices and completion.choices[0].message:
                    return f"✅ 连接成功！响应时间: {response_time:.2f}秒"
                else:
                    return f"❌ 模型响应异常"

            except Exception as api_error:
                error_msg = str(api_error)
                if "401" in error_msg or "Unauthorized" in error_msg:
                    return f"❌ API密钥无效"
                elif "404" in error_msg or "not found" in error_msg:
                    return f"❌ 模型不存在: {model_config['name']}"
                elif "timeout" in error_msg.lower():
                    return f"❌ 连接超时"
                else:
                    return f"❌ 连接失败: {error_msg[:50]}..."

        except Exception as e:
            return f"❌ 测试失败: {str(e)[:50]}..."

    def _create_task_tab(self):
        """创建任务处理标签页"""

        # 获取初始选择（优先默认模型，其次上次选择）
        initial_selection = self.config_service.get_initial_selection()
        initial_provider = initial_selection.get("provider")
        initial_model = initial_selection.get("model")
        selection_source = initial_selection.get("source", "")

        with gr.Row():
            with gr.Column(scale=1):
                # 显示当前选择来源
                source_text = "📌 默认模型" if selection_source == "default" else "📝 上次选择" if selection_source == "last_choice" else ""
                header_html = f"<h3 style='text-align: center; color: #2d3748; font-size: 17px; padding: 10px; background: #f7f8fa; border-radius: 8px; margin-bottom: 15px;'>🤖 模型配置 {source_text}</h3>"
                gr.HTML(header_html)

                providers = list(self.config_service.get_all_providers().keys())
                provider_dropdown = gr.Dropdown(
                    label="云平台",
                    choices=[(self.config_service.get_provider_info(p)['info']['display_name'], p)
                             for p in providers],
                    value=initial_provider if initial_provider in providers else (providers[0] if providers else None)
                )

                # 根据初始选择的云平台获取模型列表
                selected_provider = initial_provider if initial_provider in providers else (
                    providers[0] if providers else None)
                initial_models = {}
                if selected_provider:
                    initial_models = self.config_service.get_models_by_provider(selected_provider)
                    initial_model_choices = [(info.get('name', key), key)
                                             for key, info in initial_models.items()]
                else:
                    initial_model_choices = []

                # 确定初始模型值
                initial_model_value = None
                if initial_model and any(key == initial_model for _, key in initial_model_choices):
                    initial_model_value = initial_model
                elif initial_model_choices:
                    initial_model_value = initial_model_choices[0][1]

                model_dropdown = gr.Dropdown(
                    label="模型",
                    choices=initial_model_choices,
                    value=initial_model_value
                )

                prompts = self.config_service.get_all_prompts()
                prompt_choices = [(p['name'], p['id']) for p in prompts]

                # 优先选择 default 提示词
                default_prompt_value = None
                for name, pid in prompt_choices:
                    if pid == "default":
                        default_prompt_value = pid
                        break
                if not default_prompt_value and prompt_choices:
                    default_prompt_value = prompt_choices[0][1]

                prompt_dropdown = gr.Dropdown(
                    label="提示词模板",
                    choices=prompt_choices,
                    value=default_prompt_value
                )

                with gr.Accordion("⚙️ 高级设置", open=False):
                    max_workers = gr.Slider(label="并发数", minimum=1, maximum=5, value=2, step=1)
                    max_retries = gr.Slider(label="重试次数", minimum=0, maximum=3, value=2, step=1)
                    request_delay = gr.Slider(label="请求间隔(秒)", minimum=0, maximum=2, value=0.0, step=0.1)
                    enable_compression = gr.Checkbox(label="启用图片压缩", value=True)

            with gr.Column(scale=1):
                gr.HTML(
                    "<h3 style='text-align: center; color: #2d3748; font-size: 17px; padding: 10px; background: #f7f8fa; border-radius: 8px; margin-bottom: 15px;'>📁 文件上传</h3>")

                files_upload = gr.File(
                    label="选择图片文件",
                    file_count="multiple",
                    file_types=["image"],
                    height=200
                )

                with gr.Row():
                    test_connection_btn = gr.Button("🧪 测试连接")
                    clear_files_btn = gr.Button("🗑️ 清空文件")

        # 处理按钮
        process_btn = gr.Button("🚀 开始处理", variant="primary")

        # 结果显示
        gr.HTML(
            "<h3 style='text-align: center; color: #2d3748; font-size: 17px; padding: 10px; background: #f7f8fa; border-radius: 8px; margin: 15px 0;'>📊 处理结果</h3>")
        status_display = gr.HTML("<div class='status-card waiting'>⏳ 等待任务开始...</div>")
        timer_display = gr.HTML("")
        result_display = gr.JSON(label="详细结果", value={"提示": "等待处理结果..."})

        # 事件绑定
        def update_models(provider_key):
            if not provider_key:
                return gr.update(choices=[], value=None)

            models = self.config_service.get_models_by_provider(provider_key)
            model_choices = [(info.get('name', key), key)
                             for key, info in models.items()]
            return gr.update(choices=model_choices,
                             value=model_choices[0][1] if model_choices else None)

        def test_connection(provider_key, model_key):
            if not provider_key or not model_key:
                return "❌ 请选择云平台和模型"
            return self._test_single_connection(provider_key, model_key)

        def clear_files():
            return None, "<div style='color: #6c757d; padding: 10px;'>🗑️ 文件已清空</div>", ""

        def format_duration(seconds: float) -> str:
            """格式化时间显示，保持固定宽度避免跳动"""
            seconds = max(0.0, float(seconds))
            total = int(seconds)
            hh = total // 3600
            mm = (total % 3600) // 60
            ss = total % 60
            if hh > 0:
                return f"{hh:02d}:{mm:02d}:{ss:02d}"
            return f"{mm:02d}:{ss:02d}"

        def build_status_html(status_type: str, title: str, stats: dict = None, output_dir: str = None) -> str:
            """构建状态卡片 HTML"""
            if status_type == "processing":
                return f'''
                <div style="background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%); border-left: 4px solid #ffc107; border-radius: 8px; padding: 16px; margin: 10px 0;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 28px;">⏳</span>
                        <span style="font-size: 18px; font-weight: 600; color: #856404;">{title}</span>
                    </div>
                </div>
                '''
            elif status_type == "success":
                stats_html = ""
                if stats:
                    stats_html = f'''
                    <div style="display: flex; align-items: center; gap: 12px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #c3e6cb;">
                        <span style="font-size: 24px;">📊</span>
                        <span style="color: #155724;">
                            成功: <strong>{stats.get("success", 0)}</strong> 张 | 
                            失败: <strong>{stats.get("failed", 0)}</strong> 张 | 
                            总计: <strong>{stats.get("total", 0)}</strong> 张
                        </span>
                    </div>
                    '''
                dir_html = ""
                if output_dir:
                    dir_html = f'''
                    <div style="margin-top: 8px; padding: 8px 12px; background: #e8f5e9; border-radius: 4px; font-size: 13px; color: #2e7d32; word-break: break-all;">
                        📁 输出目录: {output_dir}
                    </div>
                    '''
                return f'''
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-left: 4px solid #28a745; border-radius: 8px; padding: 16px; margin: 10px 0;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 28px;">✅</span>
                        <span style="font-size: 18px; font-weight: 600; color: #155724;">{title}</span>
                    </div>
                    {stats_html}
                    {dir_html}
                </div>
                '''
            elif status_type == "error":
                return f'''
                <div style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); border-left: 4px solid #dc3545; border-radius: 8px; padding: 16px; margin: 10px 0;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 28px;">❌</span>
                        <span style="font-size: 18px; font-weight: 600; color: #721c24;">{title}</span>
                    </div>
                </div>
                '''
            return f'<div>{title}</div>'

        def build_timer_html(started_at: datetime, elapsed: float, finished_at: datetime = None,
                             timings: dict = None) -> str:
            """构建计时器卡片 HTML"""
            time_rows = f'''
                <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #e9ecef;">
                    <span style="color: #6c757d;">开始时间</span>
                    <span style="font-weight: 500; font-family: 'Consolas', monospace;">{started_at.strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
            '''
            if finished_at:
                time_rows += f'''
                <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #e9ecef;">
                    <span style="color: #6c757d;">结束时间</span>
                    <span style="font-weight: 500; font-family: 'Consolas', monospace;">{finished_at.strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 6px 0;">
                    <span style="color: #6c757d;">总耗时</span>
                    <span style="font-weight: 600; color: #667eea; font-family: 'Consolas', monospace; font-size: 16px;">{format_duration(elapsed)}</span>
                </div>
                '''
            else:
                time_rows += f'''
                <div style="display: flex; justify-content: space-between; padding: 6px 0;">
                    <span style="color: #6c757d;">已用时间</span>
                    <span style="font-weight: 600; color: #667eea; font-family: 'Consolas', monospace; font-size: 16px;">{format_duration(elapsed)}</span>
                </div>
                '''

            timings_html = ""
            if timings:
                timing_items = []
                labels = {
                    "preprocess_seconds": "预处理",
                    "api_seconds": "API调用",
                    "parse_seconds": "解析结果",
                    "save_seconds": "保存文件"
                }
                for k in ("preprocess_seconds", "api_seconds", "parse_seconds", "save_seconds"):
                    if k in timings:
                        label = labels.get(k, k)
                        timing_items.append(
                            f'<span style="background: #e9ecef; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{label}: {timings[k]}s</span>')
                if timing_items:
                    timings_html = f'''
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #dee2e6;">
                        <div style="color: #6c757d; font-size: 13px; margin-bottom: 8px;">⏱️ 耗时拆分</div>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            {"".join(timing_items)}
                        </div>
                    </div>
                    '''

            return f'''
            <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 16px; margin: 10px 0;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span style="font-size: 18px;">🕐</span>
                    <span style="font-weight: 600; color: #495057;">时间信息</span>
                </div>
                {time_rows}
                {timings_html}
            </div>
            '''

        def process_task(provider_key, model_key, prompt_id, files, max_workers, max_retries, request_delay,
                         enable_compression):
            if not all([provider_key, model_key, prompt_id, files]):
                return build_status_html("error", "请完整填写所有参数"), "", {"错误": "请完整填写所有参数"}

            try:
                prompt_data = self.config_service.get_prompt_by_id(prompt_id)
                if not prompt_data:
                    return build_status_html("error", "提示词不存在"), "", {"错误": "提示词不存在"}

                prompt_text = prompt_data["prompt"]

                image_paths = [Path(f.name) for f in files] if isinstance(files, list) else [Path(files.name)]
                file_count = len(image_paths)

                started_at = datetime.now()
                t0 = time.perf_counter()

                result_holder = {"result": None, "error": None}

                def _run_processing():
                    try:
                        result_holder["result"] = self.processor.process(
                            provider_key=provider_key,
                            model_key=model_key,
                            images=image_paths,
                            prompt=prompt_text,
                            max_workers=int(max_workers),
                            max_retries=int(max_retries),
                            request_delay=float(request_delay),
                            enable_compression=enable_compression,
                            verbose=False,
                        )
                    except Exception as e:
                        result_holder["error"] = e

                thread = threading.Thread(target=_run_processing, daemon=True)
                thread.start()

                # 初始状态
                status_html = build_status_html("processing", f"正在处理 {file_count} 张图片...")
                timer_html = build_timer_html(started_at, 0.0)
                yield (status_html, timer_html, gr.update())

                # 轮询更新计时器（每秒一次）
                while thread.is_alive():
                    time.sleep(1)
                    elapsed = time.perf_counter() - t0
                    timer_html = build_timer_html(started_at, elapsed)
                    yield (gr.update(), timer_html, gr.update())

                finished_at = datetime.now()
                elapsed = time.perf_counter() - t0

                if result_holder["error"] is not None:
                    self.config_service.add_task_record(
                        provider=provider_key,
                        model=model_key,
                        file_count=file_count,
                        success_count=0,
                        failed_count=file_count,
                    )
                    err = str(result_holder["error"])
                    timer_html = build_timer_html(started_at, elapsed, finished_at)
                    yield build_status_html("error", f"处理失败: {err}"), timer_html, {"错误": f"处理失败: {err}"}
                    return

                result = result_holder["result"] or {}

                success_count = 0
                failed_count = 0
                output_dir = None

                if "summary" in result:
                    summary = result["summary"]
                    totals = summary.get("totals", {})
                    success_count = totals.get("success", 0)
                    failed_count = totals.get("failed", 0)
                    output_dir = summary.get("output_dir")

                self.config_service.add_task_record(
                    provider=provider_key,
                    model=model_key,
                    file_count=file_count,
                    success_count=success_count,
                    failed_count=failed_count,
                    output_dir=output_dir,
                )

                # 获取耗时拆分
                timings = {}
                try:
                    timings = (result.get("summary", {}) or {}).get("images", [{}])[0].get("timings", {}) or {}
                except Exception:
                    pass

                # 构建最终状态
                stats = {"success": success_count, "failed": failed_count, "total": file_count}
                status_html = build_status_html("success", "处理完成！", stats, output_dir)
                timer_html = build_timer_html(started_at, elapsed, finished_at, timings)

                yield status_html, timer_html, result

            except Exception as e:
                file_count = len(files) if isinstance(files, list) else 1
                self.config_service.add_task_record(
                    provider=provider_key,
                    model=model_key,
                    file_count=file_count,
                    success_count=0,
                    failed_count=file_count,
                )
                return build_status_html("error", f"处理失败: {str(e)}"), "", {"错误": f"处理失败: {str(e)}"}

        provider_dropdown.change(fn=update_models, inputs=[provider_dropdown], outputs=[model_dropdown])
        test_connection_btn.click(fn=test_connection, inputs=[provider_dropdown, model_dropdown],
                                  outputs=[status_display])
        clear_files_btn.click(fn=clear_files, outputs=[files_upload, status_display, timer_display])
        click_kwargs = {
            "fn": process_task,
            "inputs": [provider_dropdown, model_dropdown, prompt_dropdown, files_upload,
                       max_workers, max_retries, request_delay, enable_compression],
            "outputs": [status_display, timer_display, result_display],
        }
        # 使用 Gradio 原生进度显示（含计时/ETA），避免自定义计时闪烁
        try:
            import inspect as _inspect
            if "show_progress" in _inspect.signature(process_btn.click).parameters:
                click_kwargs["show_progress"] = "hidden"
        except Exception:
            pass
        process_btn.click(**click_kwargs)

    def _create_model_tab(self):
        """创建模型管理标签页"""

        with gr.Row():
            with gr.Column(scale=1):
                providers = list(self.config_service.get_all_providers().keys())
                mgmt_provider_dropdown = gr.Dropdown(
                    label="云平台",
                    choices=[(self.config_service.get_provider_info(p)['info']['display_name'], p)
                             for p in providers],
                    value=providers[0] if providers else None
                )

                initial_mgmt_models = []
                if providers:
                    initial_mgmt_models = self.config_service.get_models_by_provider(providers[0])
                    initial_mgmt_model_choices = [(info.get('name', key), key)
                                                  for key, info in initial_mgmt_models.items()]
                else:
                    initial_mgmt_model_choices = []

                mgmt_model_dropdown = gr.Dropdown(
                    label="模型",
                    choices=initial_mgmt_model_choices,
                    value=initial_mgmt_model_choices[0][1] if initial_mgmt_model_choices else None
                )

                with gr.Row():
                    view_model_btn = gr.Button("👁️ 查看")
                    test_model_btn = gr.Button("🧪 测试", variant="primary")

                with gr.Row():
                    add_model_btn = gr.Button("➕ 添加", variant="primary")
                    edit_model_btn = gr.Button("✏️ 编辑")

                with gr.Row():
                    test_all_btn = gr.Button("🧪 测试全部")
                    refresh_btn = gr.Button("🔄 刷新")

            with gr.Column(scale=2):
                model_details = gr.JSON(label="模型详细信息", value={})

        gr.HTML("""
        <div style="text-align: center; padding: 15px; margin: 20px 0; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; border-left: 4px solid #667eea;">
            <h3 style="margin: 0; color: #2d3748; font-size: 18px;">➕ 添加/编辑模型</h3>
        </div>
        """)

        current_provider_display = gr.HTML(
            "<div style='text-align: center; padding: 10px; color: #666;'>请先选择云平台</div>")

        with gr.Row():
            with gr.Column():
                model_key_input = gr.Textbox(label="模型标识符", placeholder="例如: gpt-4-vision")
                model_name_input = gr.Textbox(label="模型名称", placeholder="例如: GPT-4 Vision")
                model_label_input = gr.Textbox(label="显示标签", placeholder="例如: GPT-4V")

            with gr.Column():
                model_info_input = gr.Textbox(label="模型描述", placeholder="例如: 支持图像理解的GPT-4模型")
                model_api_url_input = gr.Textbox(label="API地址 (可选)", placeholder="留空使用平台默认地址")
                model_env_key_input = gr.Textbox(label="环境变量 (可选)", placeholder="留空使用平台默认")

        with gr.Row():
            save_model_btn = gr.Button("💾 保存", variant="primary")
            clear_model_form_btn = gr.Button("🧹 清空")

        model_mgmt_status = gr.Markdown("")

        # 事件绑定
        def update_model_list(provider_key):
            if not provider_key:
                return gr.update(choices=[], value=None), "请先选择云平台"

            models = self.config_service.get_models_by_provider(provider_key)
            model_choices = [(info.get('name', key), key) for key, info in models.items()]

            provider_info = self.config_service.get_provider_info(provider_key)
            provider_display_name = provider_info['info']['display_name']
            provider_html = f"""
            <div style="text-align: center; padding: 12px; background: #e8f4fd; border-radius: 8px; border: 1px solid #4a90e2;">
                <span style="color: #2d3748; font-size: 15px;">📍 <strong>当前操作平台：</strong> 
                <span style="color: #4a90e2; font-weight: bold;">{provider_display_name}</span></span>
            </div>
            """

            return gr.update(choices=model_choices,
                             value=model_choices[0][1] if model_choices else None), provider_html

        def view_model_details(provider_key, model_key):
            if not provider_key or not model_key:
                return {}, ""

            try:
                models = self.config_service.get_models_by_provider(provider_key)
                if model_key in models:
                    model_info = models[model_key]
                    provider_info = self.config_service.get_provider_info(provider_key)

                    details = {
                        "provider": provider_info["info"]["display_name"],
                        "provider_key": provider_key,
                        "model_key": model_key,
                        "api_base_url": provider_info["info"].get("defaults", {}).get("api_base_url", "N/A"),
                        "env_key": provider_info["info"].get("defaults", {}).get("env_key", "N/A"),
                        **model_info
                    }
                    return details, ""
                else:
                    return {}, "❌ 模型不存在"
            except Exception as e:
                return {}, f"❌ 获取模型信息失败: {str(e)}"

        def test_all_models():
            try:
                providers = list(self.config_service.get_all_providers().keys())
                results = []

                for provider_key in providers:
                    models = self.config_service.get_models_by_provider(provider_key)
                    provider_name = self.config_service.get_provider_info(provider_key)['info']['display_name']

                    results.append(f"🏢 {provider_name}:")

                    model_keys = list(models.keys())[:3]
                    for model_key in model_keys:
                        test_result = self._test_single_connection(provider_key, model_key)
                        model_name = models[model_key].get('name', model_key)
                        if "✅" in test_result:
                            results.append(f"  ✅ {model_name}")
                        else:
                            results.append(f"  ❌ {model_name}")

                    if len(models) > 3:
                        results.append(f"  ... 还有 {len(models) - 3} 个模型")
                    results.append("")

                return "\n".join(results)
            except Exception as e:
                return f"❌ 批量测试失败: {str(e)}"

        def refresh_models():
            try:
                from src.config_loader import refresh_providers
                refresh_providers()
                return "✅ 模型列表已刷新"
            except Exception as e:
                return f"❌ 刷新失败: {str(e)}"

        def load_model_for_edit(provider_key, model_key):
            if not provider_key or not model_key:
                return "", "", "", "", "", "", "❌ 请选择要编辑的模型"

            try:
                models = self.config_service.get_models_by_provider(provider_key)
                if model_key not in models:
                    return "", "", "", "", "", "", "❌ 模型不存在"

                model_info = models[model_key]
                return (
                    model_key,
                    model_info.get('name', ''),
                    model_info.get('label', ''),
                    model_info.get('info', ''),
                    model_info.get('api_base_url', ''),
                    model_info.get('env_key', ''),
                    f"✅ 已加载模型: {model_info.get('name', model_key)}"
                )
            except Exception as e:
                return "", "", "", "", "", "", f"❌ 加载失败: {str(e)}"

        def save_model(provider_key, model_key, name, label, info, api_url, env_key):
            if not all([provider_key, model_key, name]):
                return "❌ 请填写云平台、模型标识符和模型名称", gr.update()

            try:
                model_config = {
                    "name": name,
                    "label": label or name,
                    "info": info or f"{name} 模型"
                }

                if api_url.strip():
                    model_config["api_base_url"] = api_url.strip()
                if env_key.strip():
                    model_config["env_key"] = env_key.strip()

                success, message = self.config_service.add_model(provider_key, model_key, model_config)

                if success:
                    models = self.config_service.get_models_by_provider(provider_key)
                    model_choices = [(info.get('name', key), key) for key, info in models.items()]
                    return f"✅ {message}", gr.update(choices=model_choices, value=model_key)
                else:
                    return f"❌ {message}", gr.update()
            except Exception as e:
                return f"❌ 保存失败: {str(e)}", gr.update()

        def clear_model_form():
            return "", "", "", "", "", "", "🧹 表单已清空"

        mgmt_provider_dropdown.change(fn=update_model_list, inputs=[mgmt_provider_dropdown],
                                      outputs=[mgmt_model_dropdown, current_provider_display])
        view_model_btn.click(fn=view_model_details, inputs=[mgmt_provider_dropdown, mgmt_model_dropdown],
                             outputs=[model_details, model_mgmt_status])
        test_model_btn.click(fn=lambda p, m: self._test_single_connection(p, m),
                             inputs=[mgmt_provider_dropdown, mgmt_model_dropdown], outputs=[model_mgmt_status])
        test_all_btn.click(fn=test_all_models, outputs=[model_mgmt_status])
        refresh_btn.click(fn=refresh_models, outputs=[model_mgmt_status])
        add_model_btn.click(fn=clear_model_form,
                            outputs=[model_key_input, model_name_input, model_label_input, model_info_input,
                                     model_api_url_input, model_env_key_input, model_mgmt_status])
        edit_model_btn.click(fn=load_model_for_edit, inputs=[mgmt_provider_dropdown, mgmt_model_dropdown],
                             outputs=[model_key_input, model_name_input, model_label_input, model_info_input,
                                      model_api_url_input, model_env_key_input, model_mgmt_status])
        save_model_btn.click(fn=save_model,
                             inputs=[mgmt_provider_dropdown, model_key_input, model_name_input, model_label_input,
                                     model_info_input, model_api_url_input, model_env_key_input],
                             outputs=[model_mgmt_status, mgmt_model_dropdown])
        clear_model_form_btn.click(fn=clear_model_form,
                                   outputs=[model_key_input, model_name_input, model_label_input, model_info_input,
                                            model_api_url_input, model_env_key_input, model_mgmt_status])

    def _create_prompt_tab(self):
        """创建提示词管理标签页"""

        with gr.Row():
            with gr.Column(scale=1):
                def get_prompt_choices():
                    prompts = self.config_service.get_all_prompts()
                    return [(p['name'], p['id']) for p in prompts]

                prompt_choices = get_prompt_choices()
                prompt_dropdown = gr.Dropdown(
                    label="选择提示词",
                    choices=prompt_choices,
                    value=prompt_choices[0][1] if prompt_choices else None
                )

                with gr.Row():
                    view_prompt_btn = gr.Button("👁️ 查看")
                    edit_prompt_btn = gr.Button("✏️ 编辑")

                with gr.Row():
                    delete_prompt_btn = gr.Button("🗑️ 删除", variant="stop")
                    refresh_prompt_btn = gr.Button("🔄 刷新")

            with gr.Column(scale=2):
                prompt_details = gr.JSON(label="提示词详细信息", value={})

        gr.HTML("""
        <div style="text-align: center; padding: 15px; margin: 20px 0; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; border-left: 4px solid #667eea;">
            <h3 style="margin: 0; color: #2d3748; font-size: 18px;">✏️ 编辑提示词</h3>
        </div>
        """)

        with gr.Row():
            with gr.Column():
                prompt_name_input = gr.Textbox(label="名称", placeholder="例如: 产品信息抽取")
                prompt_category_input = gr.Textbox(label="分类", placeholder="例如: 电商")
                prompt_description_input = gr.Textbox(label="描述", placeholder="简要描述提示词用途")

            with gr.Column():
                prompt_tags_input = gr.Textbox(label="标签 (逗号分隔)", placeholder="例如: 电商,产品,信息抽取")

                with gr.Row():
                    save_prompt_btn = gr.Button("💾 保存", variant="primary")
                    clear_form_btn = gr.Button("🧹 清空")

        prompt_content_input = gr.Textbox(
            label="提示词内容",
            lines=8,
            placeholder="输入完整的提示词内容...",
            max_lines=15
        )

        prompt_status = gr.Markdown("")

        # 事件绑定
        def view_prompt_details(prompt_id):
            if not prompt_id:
                return {}
            prompt_data = self.config_service.get_prompt_by_id(prompt_id)
            return prompt_data if prompt_data else {}

        def edit_prompt(prompt_id):
            if not prompt_id:
                return "", "", "", "", "", "❌ 请选择要编辑的提示词"

            prompt_data = self.config_service.get_prompt_by_id(prompt_id)
            if not prompt_data:
                return "", "", "", "", "", "❌ 提示词不存在"

            tags_str = ", ".join(prompt_data.get("tags", []))
            return (
                prompt_data.get("name", ""),
                prompt_data.get("category", ""),
                prompt_data.get("description", ""),
                prompt_data.get("prompt", ""),
                tags_str,
                f"✅ 已加载提示词: {prompt_data.get('name', '')}"
            )

        def save_prompt(name, category, description, content, tags_str):
            if not all([name, content]):
                return "❌ 请填写提示词名称和内容", gr.update()

            try:
                success, message = self.config_service.save_prompt(
                    name=name,
                    category=category or "未分类",
                    description=description or "",
                    content=content,
                    tags=[tag.strip() for tag in tags_str.split(",") if tag.strip()]
                )

                if success:
                    new_choices = get_prompt_choices()
                    return f"✅ {message}", gr.update(choices=new_choices)
                else:
                    return f"❌ {message}", gr.update()
            except Exception as e:
                return f"❌ 保存失败: {str(e)}", gr.update()

        def delete_prompt(prompt_id):
            if not prompt_id:
                return "❌ 请选择要删除的提示词", gr.update()

            try:
                success, message = self.config_service.delete_prompt(prompt_id)
                if success:
                    new_choices = get_prompt_choices()
                    return f"✅ {message}", gr.update(choices=new_choices, value=None)
                else:
                    return f"❌ {message}", gr.update()
            except Exception as e:
                return f"❌ 删除失败: {str(e)}", gr.update()

        def clear_form():
            return "", "", "", "", "", "🧹 表单已清空"

        view_prompt_btn.click(fn=view_prompt_details, inputs=[prompt_dropdown], outputs=[prompt_details])
        edit_prompt_btn.click(fn=edit_prompt, inputs=[prompt_dropdown],
                              outputs=[prompt_name_input, prompt_category_input, prompt_description_input,
                                       prompt_content_input, prompt_tags_input, prompt_status])
        save_prompt_btn.click(fn=save_prompt,
                              inputs=[prompt_name_input, prompt_category_input, prompt_description_input,
                                      prompt_content_input, prompt_tags_input],
                              outputs=[prompt_status, prompt_dropdown])
        delete_prompt_btn.click(fn=delete_prompt, inputs=[prompt_dropdown], outputs=[prompt_status, prompt_dropdown])
        clear_form_btn.click(fn=clear_form, outputs=[prompt_name_input, prompt_category_input, prompt_description_input,
                                                     prompt_content_input, prompt_tags_input, prompt_status])

    def _create_history_tab(self):
        """创建任务历史标签页"""

        def get_history_display():
            history = self.config_service.get_task_history()
            stats = self.config_service.get_history_statistics()

            if not history:
                return """
<div style="text-align: center; padding: 60px 20px; color: #6c757d;">
    <div style="font-size: 64px; margin-bottom: 16px;">📭</div>
    <h3 style="margin: 0; color: #495057;">暂无历史记录</h3>
    <p style="margin: 12px 0 0 0;">完成任务后，历史记录将显示在这里</p>
</div>
"""

            # 统计概览卡片
            html = f"""
<div style="margin-bottom: 24px;">
    <h3 style="text-align: center; color: #4a5568; margin-bottom: 16px;">📊 统计概览</h3>
    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
            <div style="font-size: 28px; font-weight: 700;">{stats['total_tasks']}</div>
            <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">总任务数</div>
        </div>
        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(67, 233, 123, 0.3);">
            <div style="font-size: 28px; font-weight: 700;">{stats['success_rate']:.1f}%</div>
            <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">成功率</div>
        </div>
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);">
            <div style="font-size: 28px; font-weight: 700;">{stats['total_files']}</div>
            <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">处理文件</div>
        </div>
        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(250, 112, 154, 0.3);">
            <div style="font-size: 16px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{stats['most_used_provider'] or '-'}</div>
            <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">常用平台</div>
        </div>
        <div style="background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(161, 140, 209, 0.3);">
            <div style="font-size: 14px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{stats['most_used_model'] or '-'}</div>
            <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">常用模型</div>
        </div>
    </div>
</div>

<h3 style="text-align: center; color: #4a5568; margin: 24px 0 16px 0;">📅 最近任务</h3>
<div style="display: flex; flex-direction: column; gap: 12px;">
"""

            # 任务卡片
            for i, record in enumerate(history[:10], 1):
                is_success = record.get("success", False)
                timestamp = record.get('timestamp', 'N/A')[:19].replace('T', ' ')
                provider = record.get('provider', 'N/A')
                model = record.get('model', 'N/A')
                file_count = record.get('file_count', 0)
                success_count = record.get('success_count', 0)
                
                if is_success:
                    bg_color = "linear-gradient(135deg, #f0fff4 0%, #e6ffed 100%)"
                    border_color = "#48bb78"
                    status_icon = "✅"
                    status_text = "成功"
                    status_bg = "#48bb78"
                else:
                    bg_color = "linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%)"
                    border_color = "#f56565"
                    status_icon = "❌"
                    status_text = "失败"
                    status_bg = "#f56565"

                html += f"""
    <div style="background: {bg_color}; border-left: 4px solid {border_color}; border-radius: 10px; padding: 16px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="font-size: 24px;">{status_icon}</div>
            <div>
                <div style="font-weight: 600; color: #2d3748; font-size: 15px;">{provider} / {model}</div>
                <div style="color: #718096; font-size: 13px; margin-top: 4px;">🕐 {timestamp}</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="text-align: center; padding: 8px 16px; background: rgba(255,255,255,0.7); border-radius: 8px;">
                <div style="font-size: 18px; font-weight: 700; color: #2d3748;">{success_count}/{file_count}</div>
                <div style="font-size: 11px; color: #718096;">处理文件</div>
            </div>
            <div style="background: {status_bg}; color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{status_text}</div>
        </div>
    </div>
"""

            html += "</div>"
            return html

        history_display = gr.HTML(get_history_display())

        with gr.Row():
            refresh_history_btn = gr.Button("🔄 刷新", variant="primary")
            clear_history_btn = gr.Button("🗑️ 清空历史", variant="stop")

        def clear_history():
            success, message = self.config_service.clear_task_history()
            if success:
                return get_history_display(), f"✅ {message}"
            else:
                return get_history_display(), f"❌ {message}"

        status_msg = gr.Markdown("")
        refresh_history_btn.click(fn=get_history_display, outputs=[history_display])
        clear_history_btn.click(fn=clear_history, outputs=[history_display, status_msg])

    def _create_settings_tab(self):
        """创建系统设置标签页"""

        gr.HTML("""
        <div style="text-align: center; padding: 15px; margin-bottom: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; border-left: 4px solid #667eea;">
            <h3 style="margin: 0; color: #2d3748; font-size: 18px;">🔑 API 密钥配置</h3>
        </div>
        """)

        def get_api_status():
            status = self.config_service.get_system_status()

            status_text = "#### 当前 API 密钥状态\n\n"
            for name, info_data in status["api_keys"].items():
                status_icon = "✅" if info_data["configured"] else "❌"
                status_text += f"**{status_icon} {name}**\n"
                status_text += f"- 环境变量: `{info_data['env_key']}`\n"
                status_text += f"- 状态: {'已配置' if info_data['configured'] else '未配置'}\n\n"

            return status_text

        api_status_display = gr.Markdown(get_api_status())

        gr.Markdown("""
### 🛠️ 如何设置环境变量

**Windows (PowerShell)**:
```
$env:DASHSCOPE_API_KEY="your_api_key_here"
$env:ARK_API_KEY="your_api_key_here"
$env:MODELSCOPE_ACCESS_TOKEN="your_token_here"
$env:HUNYUAN_API_KEY="your_api_key_here"
```

**Linux/macOS**:
```
export DASHSCOPE_API_KEY="your_api_key_here"
export ARK_API_KEY="your_api_key_here"
export MODELSCOPE_ACCESS_TOKEN="your_token_here"
export HUNYUAN_API_KEY="your_api_key_here"
```
""")

        gr.HTML("""
        <div style="text-align: center; padding: 15px; margin: 20px 0; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; border-left: 4px solid #667eea;">
            <h3 style="margin: 0; color: #2d3748; font-size: 18px;">💻 系统信息</h3>
        </div>
        """)

        def get_system_info():
            status = self.config_service.get_system_status()

            info = "#### 📁 目录状态\n"
            for name, dir_info in status["directories"].items():
                status_text = "✅ 存在" if dir_info["exists"] else "❌ 不存在"
                info += f"- **{name}**: {status_text} (`{dir_info['path']}`)\n"

            info += "\n#### 📄 配置文件状态\n"
            for name, exists in status["config_files"].items():
                status_text = "✅ 存在" if exists else "❌ 不存在"
                info += f"- **{name}**: {status_text}\n"

            return info

        system_info_display = gr.Markdown(get_system_info())

        with gr.Row():
            refresh_api_btn = gr.Button("🔄 刷新API状态", variant="primary")
            refresh_system_btn = gr.Button("💻 刷新系统信息")

        refresh_api_btn.click(fn=get_api_status, outputs=[api_status_display])
        refresh_system_btn.click(fn=get_system_info, outputs=[system_info_display])

        # ==================== 默认模型设置 ====================
        gr.HTML("""
        <div style="text-align: center; padding: 15px; margin: 20px 0; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; border-left: 4px solid #28a745;">
            <h3 style="margin: 0; color: #2d3748; font-size: 18px;">📌 默认模型设置</h3>
            <p style="margin: 8px 0 0 0; color: #666; font-size: 13px;">设置后，Web页面启动时会直接使用此模型（优先级高于上次选择）</p>
        </div>
        """)

        def get_default_model_status():
            default_model = self.config_service.get_default_model()
            if default_model:
                provider_key = default_model["provider"]
                model_key = default_model["model"]
                try:
                    provider_info = self.config_service.get_provider_info(provider_key)
                    models = self.config_service.get_models_by_provider(provider_key)
                    provider_name = provider_info['info']['display_name']
                    model_name = models.get(model_key, {}).get('name', model_key)
                    return f"✅ **当前默认模型**: {provider_name} / {model_name}"
                except Exception:
                    return f"✅ **当前默认模型**: {provider_key} / {model_key}"
            else:
                return "📝 **未设置默认模型**，将使用上次选择的模型"

        default_model_status = gr.Markdown(get_default_model_status())

        with gr.Row():
            with gr.Column():
                providers = list(self.config_service.get_all_providers().keys())
                default_provider_dropdown = gr.Dropdown(
                    label="选择云平台",
                    choices=[(self.config_service.get_provider_info(p)['info']['display_name'], p)
                             for p in providers],
                    value=providers[0] if providers else None
                )

            with gr.Column():
                initial_models = self.config_service.get_models_by_provider(providers[0]) if providers else {}
                initial_model_choices = [(info.get('name', key), key) for key, info in initial_models.items()]

                default_model_dropdown = gr.Dropdown(
                    label="选择模型",
                    choices=initial_model_choices,
                    value=initial_model_choices[0][1] if initial_model_choices else None
                )

        with gr.Row():
            set_default_btn = gr.Button("📌 设为默认", variant="primary")
            clear_default_btn = gr.Button("🗑️ 清除默认")

        default_model_result = gr.Markdown("")

        def update_default_models(provider_key):
            if not provider_key:
                return gr.update(choices=[], value=None)
            models = self.config_service.get_models_by_provider(provider_key)
            model_choices = [(info.get('name', key), key) for key, info in models.items()]
            return gr.update(choices=model_choices, value=model_choices[0][1] if model_choices else None)

        def set_default_model(provider_key, model_key):
            if not provider_key or not model_key:
                return "❌ 请选择云平台和模型", get_default_model_status()
            success, msg = self.config_service.set_default_model(provider_key, model_key)
            return f"{'✅' if success else '❌'} {msg}", get_default_model_status()

        def clear_default_model():
            success, msg = self.config_service.clear_default_model()
            return f"{'✅' if success else '❌'} {msg}", get_default_model_status()

        default_provider_dropdown.change(fn=update_default_models, inputs=[default_provider_dropdown],
                                         outputs=[default_model_dropdown])
        set_default_btn.click(fn=set_default_model, inputs=[default_provider_dropdown, default_model_dropdown],
                              outputs=[default_model_result, default_model_status])
        clear_default_btn.click(fn=clear_default_model, outputs=[default_model_result, default_model_status])


def create_web_app() -> gr.Blocks:
    """创建 Web 应用实例"""
    app = WebApp()
    return app.create_app()


if __name__ == "__main__":
    app = create_web_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=7863,
        share=False,
        show_error=True
    )
