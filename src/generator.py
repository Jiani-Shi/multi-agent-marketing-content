# src/generator.py

import json
import re
from typing import Dict, Any, Optional, List

from langchain_core.messages import HumanMessage, SystemMessage

from .router import get_agent


class ContentGenerator:
    """多平台营销内容生成器（基于 Agent 架构）"""

    def generate(
        self,
        product_name: str,
        core_benefits: str,
        target_audience: str,
        platform: str,
        tone_name: Optional[str] = None,
        additional_info: str = "",
        promotion_info: str = "",
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        生成单平台营销内容

        参数:
            promotion_info: 促销信息（选填），如"买一送一""限时立减50元"等
        """
        agent = get_agent(platform)

        tone_instruction = f"用户指定调性：{tone_name}" if tone_name else "请自动匹配最合适的调性"

        if promotion_info.strip():
            promotion_text = f"促销信息（用户已提供，可以使用）：{promotion_info}"
        else:
            promotion_text = "促销信息：用户未提供。严禁在文案中出现任何促销相关内容（如赠品、折扣、活动、库存紧迫感等）。"

        user_input = f"""
请为以下产品生成 {platform} 平台营销文案：

产品名称：{product_name}
核心卖点：{core_benefits}
目标人群：{target_audience}
{tone_instruction}
{promotion_text}
{additional_info if additional_info else ""}

请先调用工具检索参考案例和调性约束，分析后再生成文案。
重要：只输出 JSON，不要有任何其他文字。
"""

        messages = [
            HumanMessage(content=user_input)
        ]

        result = agent.invoke({"messages": messages})

        output_text = ""
        if isinstance(result, dict) and "messages" in result:
            last_message = result["messages"][-1]
            output_text = last_message.content if hasattr(last_message, "content") else str(last_message)
        else:
            output_text = str(result)

        parsed = self._parse_response(output_text)

        return {
            "platform": platform,
            "title": parsed.get("title", ""),
            "content": parsed.get("content", output_text[:500]),
            "tone_used": tone_name if tone_name else "自动匹配"
        }

    def generate_all_platforms(
        self,
        product_name: str,
        core_benefits: str,
        target_audience: str,
        platforms: Optional[List[str]] = None,
        tone_name: Optional[str] = None,
        additional_info: str = "",
        promotion_info: str = ""
    ) -> Dict[str, Any]:
        """批量生成所有平台内容"""
        if platforms is None:
            from .config import PLATFORMS
            platforms = PLATFORMS

        results = {}
        for platform in platforms:
            print(f"正在生成 {platform} 平台内容...")
            try:
                result = self.generate(
                    product_name=product_name,
                    core_benefits=core_benefits,
                    target_audience=target_audience,
                    platform=platform,
                    tone_name=tone_name,
                    additional_info=additional_info,
                    promotion_info=promotion_info
                )
                results[platform] = result
                print(f"√ {platform} 生成完成")
            except Exception as e:
                print(f"× {platform} 生成失败: {e}")
                results[platform] = {"error": str(e)}

        return results

    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """解析 LLM 返回的 JSON，带多重兜底策略"""

        # 策略一：直接解析
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            pass

        # 策略二：提取最外层花括号内容
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # 策略三：正则匹配 title 和 content 字段
        try:
            title_match = re.search(r'"title"\s*:\s*"([^"]*)"', response_text)
            content_match = re.search(r'"content"\s*:\s*"([^"]*)"', response_text, re.DOTALL)

            if title_match or content_match:
                return {
                    "title": title_match.group(1) if title_match else "生成失败",
                    "content": content_match.group(1) if content_match else response_text[:500]
                }
        except Exception:
            pass

        # 策略四：全部失败，返回原文
        return {
            "title": "解析失败",
            "content": response_text[:500] + ("..." if len(response_text) > 500 else "")
        }


if __name__ == "__main__":
    generator = ContentGenerator()

    print("测试1：无促销信息（验证不会编造）")
    print("-" * 40)
    result1 = generator.generate(
        product_name="谷雨美白奶罐",
        core_benefits="去黄提亮、温和不刺激",
        target_audience="熬夜党、肤色暗沉人群",
        platform="douyin",
        tone_name="治愈系温暖风",
        promotion_info=""
    )
    print(f"标题：{result1['title']}")
    print(f"正文：{result1['content'][:200]}...")

    print("\n测试2：提供促销信息（验证正确使用）")
    print("-" * 40)
    result2 = generator.generate(
        product_name="谷雨美白奶罐",
        core_benefits="去黄提亮、温和不刺激",
        target_audience="熬夜党、肤色暗沉人群",
        platform="douyin",
        tone_name="治愈系温暖风",
        promotion_info="限时买一送一，赠价值99元小样套装，活动截止本周日"
    )
    print(f"标题：{result2['title']}")
    print(f"正文：{result2['content'][:200]}...")