#!/usr/bin/env python3
"""
流式输出验收测试

验证：
1. 真实 streaming（TTFT 在正文之前出现）
2. 打字机效果（逐步打印）
3. 计时完整（TTFT / STREAM DONE / JSON / SAVE / ALL DONE）
4. JSON 解析成功
5. 失败兜底（JSON_PARSE_FAILED + .txt 备份）

运行方式：
    conda deactivate; python tests/test_streaming.py
"""

import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
src_root = project_root / "src"
sys.path.insert(0, str(src_root))
sys.path.insert(0, str(project_root))


def test_normal_json_output():
    """
    测试1：正常 JSON 输出
    
    预期结果：
    - [TIME] TTFT=x.xxxs 出现在正文之前
    - 正文逐步打印（打字机效果）
    - [TIME] gen=x.xxxs total=x.xxxs chars=xxx
    - [JSON] parse=x.xxxs valid=True
    - [SAVE] save=x.xxxs path=xxx
    - [TIME] all=x.xxxs
    """
    print("=" * 60)
    print("测试1：正常 JSON 输出")
    print("=" * 60)
    print()
    print("请确保：")
    print("1. data/inputs/ 目录下有至少一张图片")
    print("2. 已配置 API 密钥（如 MODELSCOPE_ACCESS_TOKEN）")
    print()
    print("运行命令：")
    print("    conda deactivate; python run_cli.py --select")
    print()
    print("验收标准：")
    print("  ✓ [TIME] TTFT=x.xxxs 出现在模型输出之前")
    print("  ✓ 模型输出是逐字打印，不是一次性出现")
    print("  ✓ 出现 [TIME] gen=... total=... chars=...")
    print("  ✓ 出现 [JSON] parse=... valid=True")
    print("  ✓ 出现 [SAVE] save=... path=...")
    print("  ✓ 出现 [TIME] all=...")
    print("  ✓ 生成的 .json 文件可正常打开")
    print()


def test_json_parse_failure():
    """
    测试2：JSON 解析失败兜底
    
    使用一个故意让模型输出非 JSON 的提示词
    """
    print("=" * 60)
    print("测试2：JSON 解析失败兜底")
    print("=" * 60)
    print()
    print("方法：修改 config/prompts/default.yml 中的提示词为：")
    print()
    print('    prompt: |')
    print('      请用中文描述这张图片的内容，不要输出JSON格式。')
    print('      直接用自然语言描述即可。')
    print()
    print("然后运行：")
    print("    conda deactivate; python run_cli.py --select")
    print()
    print("验收标准：")
    print("  ✓ 出现 [JSON] parse=... valid=False reason=...")
    print("  ✓ 出现 [ERR] JSON_PARSE_FAILED ...")
    print("  ✓ 出现 [SAVE] ... backup=xxx_backup.txt")
    print("  ✓ 生成 xxx_backup.txt 文件，包含原始输出")
    print()


def test_timing_precision():
    """
    测试3：计时精度验证
    """
    print("=" * 60)
    print("测试3：计时精度验证")
    print("=" * 60)
    print()
    print("验收标准：")
    print("  ✓ 所有时间都精确到 3 位小数（毫秒级）")
    print("  ✓ TTFT < total（首 token 时间 < 总时间）")
    print("  ✓ gen + parse + save ≈ total - TTFT")
    print("  ✓ all ≈ total + parse + save")
    print()


def run_quick_test():
    """
    快速测试：直接调用 API 验证流式功能
    """
    print("=" * 60)
    print("快速测试：直接调用流式 API")
    print("=" * 60)
    print()
    
    import os
    
    # 检查 API 密钥
    api_keys = {
        "MODELSCOPE_ACCESS_TOKEN": "魔塔 ModelScope",
        "DASHSCOPE_API_KEY": "阿里云 DashScope",
        "ARK_API_KEY": "豆包/火山方舟",
    }
    
    configured = []
    for key, name in api_keys.items():
        if os.environ.get(key):
            configured.append((key, name))
    
    if not configured:
        print("❌ 未配置任何 API 密钥")
        print("请先配置环境变量，例如：")
        print("    set MODELSCOPE_ACCESS_TOKEN=your_token")
        return
    
    print(f"✓ 已配置 {len(configured)} 个 API 密钥")
    for key, name in configured:
        print(f"  - {name} ({key})")
    print()
    
    # 检查测试图片
    test_images_dir = project_root / "data" / "inputs"
    if not test_images_dir.exists():
        print(f"❌ 测试图片目录不存在: {test_images_dir}")
        return
    
    images = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
    if not images:
        print(f"❌ 测试图片目录为空: {test_images_dir}")
        print("请放入至少一张图片")
        return
    
    print(f"✓ 找到 {len(images)} 张测试图片")
    print()
    
    print("准备就绪！请运行以下命令进行测试：")
    print()
    print("    conda deactivate; python run_cli.py --select")
    print()
    print("观察控制台输出，确认：")
    print("  1. [TIME] TTFT=... 出现在模型输出之前")
    print("  2. 模型输出是逐字打印的")
    print("  3. 所有计时日志都正确显示")
    print()


def main():
    print()
    print("=" * 60)
    print("  流式输出验收测试指南")
    print("=" * 60)
    print()
    
    test_normal_json_output()
    test_json_parse_failure()
    test_timing_precision()
    
    print("=" * 60)
    print("快速环境检查")
    print("=" * 60)
    print()
    run_quick_test()


if __name__ == "__main__":
    main()
