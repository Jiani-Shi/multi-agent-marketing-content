# app.py

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from src.generator import ContentGenerator
from src.config import PLATFORMS


# 全局实例
generator = ContentGenerator()

# 历史记录（内存存储）
history_records = []

# 平台名称映射
PLATFORM_NAMES = {
    "douyin": "抖音",
    "xiaohongshu": "小红书",
    "ecommerce": "电商",
    "wechat": "公众号"
}

# 调性选项
TONE_OPTIONS = [
    "自动匹配",
    "科技感极简风",
    "治愈系温暖风",
    "高端商务风",
    "活力潮流风",
    "亲民平价风"
]


def generate_content(
    product_name, core_benefits, target_audience,
    tone_choice, promotion_info, selected_platforms
):
    """生成内容的主函数"""

    # 输入校验
    if not product_name.strip():
        return "请填写产品名称", "", "", "", ""
    if not core_benefits.strip():
        return "请填写核心卖点", "", "", "", ""
    if not target_audience.strip():
        return "请填写目标人群", "", "", "", ""
    if not selected_platforms:
        return "请至少选择一个平台", "", "", "", ""

    # 处理调性
    tone_name = None if tone_choice == "自动匹配" else tone_choice

    # 批量生成
    results = generator.generate_all_platforms(
        product_name=product_name,
        core_benefits=core_benefits,
        target_audience=target_audience,
        platforms=selected_platforms,
        tone_name=tone_name,
        promotion_info=promotion_info
    )

    # 记录历史
    history_records.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "product_name": product_name,
        "platforms": [PLATFORM_NAMES.get(p, p) for p in selected_platforms],
        "results": results
    })

    # 格式化输出
    outputs = []
    for platform in ["douyin", "xiaohongshu", "ecommerce", "wechat"]:
        if platform in results and "error" not in results[platform]:
            r = results[platform]
            text = f"标题：{r['title']}\n\n正文：\n{r['content']}"
            outputs.append(text)
        elif platform in results:
            outputs.append(f"生成失败：{results[platform]['error']}")
        else:
            outputs.append("（未选择此平台）")

    status = f"生成完成，共 {len(selected_platforms)} 个平台"
    return status, outputs[0], outputs[1], outputs[2], outputs[3]


def get_history():
    """获取历史记录"""
    if not history_records:
        return "暂无历史记录"

    text = ""
    for i, record in enumerate(reversed(history_records[-10:]), 1):
        text += f"""
记录 {i} | {record['time']}
产品：{record['product_name']}
平台：{', '.join(record['platforms'])}
{'-' * 40}
"""
    return text


def clear_history():
    """清空历史记录"""
    history_records.clear()
    return "历史记录已清空"


# 构建界面
CSS = """
.gradio-container {
    max-width: 100% !important;
    min-height: 100vh !important;
    padding: 0 !important;
    font-size: 14px !important;
}
.gradio-container > .wrap {
    max-width: 100% !important;
    padding: 1% 2% !important;
    min-height: 100vh !important;
}
.gr-row {
    display: flex !important;
    flex-direction: row !important;
    gap: 16px !important;
    flex: 1 !important;
    min-height: calc(100vh - 120px) !important;
}
.gr-column {
    min-height: 100% !important;
}
.gr-button {
    font-size: 15px !important;
    font-weight: 600 !important;
}
.gr-tab-item {
    font-size: 14px !important;
}
.main-title h1 {
    font-size: 32px !important;
    font-weight: 800 !important;
    background-color: #f0f0f0 !important;
    padding: 16px 24px !important;
    border-radius: 10px !important;
    text-align: center !important;
    margin-bottom: 12px !important;
}
.section-title h3 {
    font-size: 25px !important;
    font-weight: 700 !important;
    margin-top: 8px !important;
    margin-bottom: 8px !important;
    color: #333 !important;
}
.gradio-container label {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #444 !important;
}
.gradio-container input {
    font-size: 18px !important;
}
/* 输入框的 textarea（卖点、促销等）：字号保持你的设置 */
.gr-input textarea {
    font-size: 18px !important;
}
/* 输出框：字号保持你的设置，随内容增长，达到最大高度后可滚动 */
.output-box textarea {
    font-size: 18px !important;
    max-height: 70vh !important;
    overflow-y: auto !important;
    resize: vertical !important;
}
.gradio-container input::placeholder,
.gradio-container textarea::placeholder {
    font-size: 15px !important;
    color: #aaa !important;
}
"""

with gr.Blocks(title="跨平台智能营销内容生成系统", css=CSS) as demo:
    gr.Markdown("# 跨平台智能营销内容生成系统", elem_classes="main-title")
    gr.Markdown("输入产品信息，一键生成多平台营销内容")

    with gr.Row():
        # 左侧输入区
        with gr.Column(scale=4):
            gr.Markdown("### 产品信息", elem_classes="section-title")
            product_name = gr.Textbox(
                label="产品名称",
                placeholder="例如：谷雨美白奶罐"
            )
            core_benefits = gr.Textbox(
                label="核心卖点",
                placeholder="例如：去黄提亮、温和不刺激，适合熬夜党",
                lines=3
            )
            target_audience = gr.Textbox(
                label="目标人群",
                placeholder="例如：熬夜党、肤色暗沉人群"
            )
            tone_choice = gr.Dropdown(
                label="品牌调性",
                choices=TONE_OPTIONS,
                value="自动匹配"
            )
            promotion_info = gr.Textbox(
                label="促销信息（选填）",
                placeholder="例如：限时买一送一，赠价值99元小样套装",
                lines=2
            )

            gr.Markdown("### 目标平台", elem_classes="section-title")
            platform_checkboxes = gr.CheckboxGroup(
                label="选择要生成的平台",
                choices=[
                    ("抖音", "douyin"),
                    ("小红书", "xiaohongshu"),
                    ("电商", "ecommerce"),
                    ("公众号", "wechat")
                ],
                value=["douyin", "xiaohongshu"]
            )

            generate_btn = gr.Button("生成营销内容", variant="primary", size="lg")
            status_text = gr.Textbox(label="状态", interactive=False)

        # 右侧输出区
        with gr.Column(scale=6):
            gr.Markdown("### 生成结果", elem_classes="section-title")

            with gr.Tabs():
                with gr.Tab("抖音"):
                    douyin_output = gr.Textbox(
                        label="抖音文案",
                        lines=15,
                        max_lines=40,
                        interactive=False,
                        autoscroll=False,
                        elem_classes="output-box"
                    )
                with gr.Tab("小红书"):
                    xiaohongshu_output = gr.Textbox(
                        label="小红书笔记",
                        lines=15,
                        max_lines=40,
                        interactive=False,
                        autoscroll=False,
                        elem_classes="output-box"
                    )
                with gr.Tab("电商"):
                    ecommerce_output = gr.Textbox(
                        label="电商详情页",
                        lines=15,
                        max_lines=40,
                        interactive=False,
                        autoscroll=False,
                        elem_classes="output-box"
                    )
                with gr.Tab("公众号"):
                    wechat_output = gr.Textbox(
                        label="公众号推文",
                        lines=15,
                        max_lines=40,
                        interactive=False,
                        autoscroll=False,
                        elem_classes="output-box"
                    )

            with gr.Accordion("历史记录", open=False):
                history_display = gr.Textbox(
                    label="最近10条记录",
                    lines=12,
                    interactive=False
                )
                with gr.Row():
                    refresh_history_btn = gr.Button("刷新历史")
                    clear_history_btn = gr.Button("清空历史")

    # 绑定事件
    generate_btn.click(
        fn=generate_content,
        inputs=[
            product_name, core_benefits, target_audience,
            tone_choice, promotion_info, platform_checkboxes
        ],
        outputs=[
            status_text,
            douyin_output, xiaohongshu_output,
            ecommerce_output, wechat_output
        ]
    )

    refresh_history_btn.click(fn=get_history, outputs=history_display)
    clear_history_btn.click(fn=clear_history, outputs=history_display)


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
