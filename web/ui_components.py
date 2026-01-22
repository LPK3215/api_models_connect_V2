"""
Web UI 组件模块
包含CSS样式和HTML模板
"""

# 完整样式：防抖动 + 色彩 + 标签导航 + 按钮 + 标题
CUSTOM_CSS = """
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
    background: #f7f8fa !important;
    border-bottom: 1px solid #ddd !important;
    padding: 12px 0 !important;
}

/* 标签按钮 - 字体放大 */
button[role="tab"] {
    margin: 0 10px !important;
    padding: 14px 28px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    border: none !important;
    background: transparent !important;
    color: #444 !important;
    transition: all 0.2s !important;
}

button[role="tab"]:hover {
    background: #e8e8e8 !important;
}

/* 选中的标签页 */
button[aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4) !important;
}

/* === 页面内标题居中 === */
.markdown h3, .markdown h4,
.gr-markdown h3, .gr-markdown h4 {
    text-align: center !important;
    color: #2d3748 !important;
    margin: 20px 0 !important;
}

/* === 按钮样式 === */
button.primary, .gradio-button.primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    transition: all 0.2s !important;
}

button.primary:hover {
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    transform: translateY(-1px) !important;
}

button.secondary, .gradio-button.secondary {
    background: #f0f0f0 !important;
    color: #333 !important;
    border: 1px solid #ddd !important;
}

button.stop, .gradio-button.stop {
    background: #ef4444 !important;
    border: none !important;
}

button.stop:hover {
    background: #dc2626 !important;
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
}

/* 滚动条美化 */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #999;
}

/* 隐藏 Gradio 6.x 的进度时间显示 */
.progress-text, .eta-text, .timer {
    display: none !important;
}

/* 隐藏进度条右侧的时间文本 */
.progress-bar + span, .progress-level + span {
    display: none !important;
}
"""

# 应用头部HTML
HEADER_HTML = """
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; margin-bottom: 15px;">
    <h1 style="margin: 0; font-size: 28px; font-weight: 600;">🚀 多模态批处理管理系统</h1>
    <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 14px;">统一管理云平台模型，批量处理图片任务，提取结构化信息</p>
</div>
"""

# 底部说明HTML
FOOTER_HTML = """
<div style="margin-top: 15px; padding: 12px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 8px; border: 1px solid #dee2e6; text-align: center;">
    <div style="color: #495057; font-size: 13px;">
        <strong style="color: #6f42c1;">🚀 多模态批处理管理系统</strong> | 
        <span style="color: #0d6efd;">多云平台AI模型统一管理</span> | 
        <span style="color: #198754;">高效批量图片处理</span> | 
        <span style="background: linear-gradient(135deg, #28a745, #20c997); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold;">v1.0</span>
        <br>
        <small style="color: #6c757d; margin-top: 4px; display: inline-block;">
            💡 首次使用请先在「系统设置」中配置API密钥，然后在「模型管理」中测试连接状态
        </small>
    </div>
</div>
"""


def create_stats_card(icon: str, value: str, label: str, gradient: str) -> str:
    """创建统计卡片HTML"""
    return f"""
    <div style="background: linear-gradient(135deg, {gradient}); color: white; padding: 20px; border-radius: 10px; text-align: center;">
        <h3 style="margin: 0; font-size: 24px;">{icon} {value}</h3>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">{label}</p>
    </div>
    """


def create_api_status_card(name: str, configured: bool, env_key: str) -> str:
    """创建API状态卡片HTML"""
    status_color = "#48bb78" if configured else "#f56565"
    status_icon = "✅" if configured else "❌"
    status_text = "已配置" if configured else "未配置"

    return f"""
    <div style="border: 2px solid {status_color}; border-radius: 8px; padding: 12px; text-align: center;">
        <div style="font-size: 18px; margin-bottom: 4px;">{status_icon}</div>
        <div style="font-weight: bold; margin-bottom: 4px;">{name}</div>
        <div style="color: {status_color}; font-size: 13px;">{status_text}</div>
        <div style="color: #718096; font-size: 11px; margin-top: 4px;">{env_key}</div>
    </div>
    """
