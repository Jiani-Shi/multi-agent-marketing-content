# src/prompts/base.py

from typing import Dict, Any, List


class BasePrompt:
    """所有平台 Prompt 模板的基类"""

    def __init__(self):
        self.platform = "base"
        self.min_content_length = 100
        self.max_content_length = 500

    def get_system_prompt(self) -> str:
        return """你是一个专业的营销内容创作者，擅长为不同平台撰写高质量的营销文案。
你的文案需要符合平台调性，能够吸引目标用户，并促进转化。"""

    def get_platform_rules(self) -> str:
        return ""

    def get_few_shot_instruction(self) -> str:
        return """【关于爆款参考的重要说明】
以下是为您提供的爆款文案参考示例。请先对每条示例进行「即时案例分析」，再开始创作。

对于每条参考示例，请在内部推理（不输出）以下问题：
1. 标题的吸引力来自哪里？（数字？情绪词？身份认同？悬念？）
2. 正文开头的钩子是什么？（痛点共鸣？场景代入？反常识？）
3. 文案的情绪节奏如何推进？（从提出问题到给出解决方案）
4. 结尾用了什么行动号召方式？（紧迫感？利益点？情感驱动？）
5. 整体结构有什么可复用的模式？

分析完成后，请综合所有参考示例的成功要素，结合您自己的创意，为新产品生成文案。

重要原则：
- 学习的是「成功逻辑」和「结构模式」，而非具体内容
- 不要复制示例中的品牌名、产品名、具体数据
- 将学到的技巧应用到新产品上，而非照搬
"""

    def get_negative_constraints(self) -> str:
        return """【禁止事项】
1. 禁止过度夸张：不要使用"史上最好""绝对第一""无人能比"等绝对化用语
2. 禁止虚假宣传：不要编造不存在的功效、数据或用户评价
3. 禁止违规词汇：不要包含平台违禁词、敏感词或低俗内容
4. 禁止抄袭：不要复制参考示例中的具体内容，只学习其结构和风格
5. 禁止诱导违规互动：不要使用"转发到三个群""不转不是中国人"等诱导性话术
"""

    def get_length_constraint(self) -> str:
        return f"""【字数约束】
- 全文控制在 {self.min_content_length} 至 {self.max_content_length} 字之间
- 标题控制在 15 字以内
- 请严格遵守此约束，不要过短或过长
"""

    def get_output_format(self) -> str:
        return """请返回 JSON 格式：
{
    "title": "文案标题",
    "content": "文案正文"
}"""

    def get_cot_steps(self) -> str:
        return """请按以下步骤思考：
1. （已在参考分析中完成）从爆款参考中提取可复用的结构模式
2. 分析目标人群的痛点和需求，确定选题角度
3. 将产品卖点融入选定的爆款结构中
4. 结合品牌调性确定语气
5. 生成标题和正文，确保字数在约束范围内"""

    def build(
        self,
        product_name: str,
        core_benefits: str,
        target_audience: str,
        tone_style: Dict[str, Any],
        viral_references: List[Dict],
        additional_info: str = ""
    ) -> Dict[str, str]:
        """组装完整的 Prompt"""
        
        reference_text = self._format_references(viral_references)
        tone_text = self._format_tone(tone_style)
        
        system = f"""{self.get_system_prompt()}

{self.get_negative_constraints()}
"""
        
        user = f"""
【平台特征】
{self.get_platform_rules()}

{self.get_few_shot_instruction()}

【爆款参考】
{reference_text}

【风格约束】
{tone_text}

【产品信息】
产品名称：{product_name}
核心卖点：{core_benefits}
目标人群：{target_audience}
{additional_info if additional_info else ""}

【写作要求】
{self.get_cot_steps()}

{self.get_length_constraint()}

{self.get_output_format()}
"""
        return {"system": system, "user": user}

    def _format_references(self, references: List[Dict]) -> str:
        if not references:
            return "（无参考样例）"
        
        text = ""
        for i, ref in enumerate(references, 1):
            metadata = ref.get("metadata", {})
            title = metadata.get("title", "无标题")
            content = ref.get("content", "")
            score = ref.get("score", 0)
            text += f"""
参考示例 {i}：（相似度：{score:.2f}）
标题：{title}
文案：{content}
---
"""
        return text

    def _format_tone(self, tone: Dict[str, Any]) -> str:
        if not tone:
            return "（无特定风格约束，请根据平台特征自由创作）"
        
        name = tone.get("tone_name", "")
        description = tone.get("description", "")
        keywords = tone.get("keywords", [])
        tone_desc = tone.get("tone", "")
        
        return f"""
调性名称：{name}
描述：{description}
关键词：{', '.join(keywords)}
语气：{tone_desc}
"""