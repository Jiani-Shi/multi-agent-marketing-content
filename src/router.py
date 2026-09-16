# src/router.py

from typing import Dict, Any
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from .config import LLM_MODEL, DASHSCOPE_API_KEY
from .retriever import DualRetriever
from .prompts import get_prompt_loader


_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = DualRetriever()
    return _retriever


def _get_llm():
    return ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=DASHSCOPE_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.85,
        max_tokens=4096
    )


def _create_tools(platform: str):
    """为指定平台创建工具集"""
    retriever = _get_retriever()
    prompt_loader = get_prompt_loader(platform)
    builder = prompt_loader()
    platform_rules = builder.get_platform_rules()

    @tool
    def search_viral_references(query: str) -> str:
        """从爆款库中检索与产品相关的爆款文案参考，返回示例和相似度得分。"""
        result = retriever.retrieve(query, top_k=3)  # 从爆款库检索出3条最相似的文案
        references = result.get("viral_examples", [])
        if not references:
            return "未找到相关爆款参考，请根据平台规则自由创作。"

        text = ""
        for i, ref in enumerate(references, 1):
            meta = ref.get("metadata", {})
            score = ref.get("score", 0)
            title = meta.get("title", "无标题")
            content = ref.get("content", "")[:300]
            text += f"""
参考 {i}（相似度：{score:.2f}）：
标题：{title}
文案：{content}...
"""
        return text

    @tool
    def search_tone_style(query: str) -> str:
        """从调性库中检索匹配的品牌调性，返回风格约束描述。"""
        result = retriever.retrieve(query, top_k=1)
        tone = result.get("tone_style", {})
        if not tone:
            return "未找到匹配的调性，请自由创作。"

        return f"""
调性名称：{tone.get("tone_name", "")}
描述：{tone.get("description", "")}
关键词：{', '.join(tone.get("keywords", []))}
语气：{tone.get("tone", "")}
"""

    @tool
    def get_platform_rules() -> str:
        """获取当前平台的文案规则和特征。"""
        return platform_rules

    return [search_viral_references, search_tone_style, get_platform_rules]


def _get_agent_system_prompt(platform: str) -> str:
    """各平台的 Agent 系统提示"""

    json_constraint = """
重要：你每次输出的最终结果必须是合法的 JSON 格式，包含 "title" 和 "content" 两个字段。
不要输出任何解释性文字、思考过程或额外内容，只输出 JSON。
JSON 格式如下：
{"title": "标题", "content": "正文"}
"""

    truthfulness_constraint = """
【信息真实性约束】
你只能使用用户提供的产品信息进行创作。严禁编造任何用户未提供的信息，包括但不限于：
- 赠品（如"送小样""买一送一""赠品套装"）
- 折扣（如"限时立减""第二件半价""到手价XX元"）
- 活动（如"618""双11""周年庆"）
- 库存紧迫感（如"仅剩XX件""最后XX份"）
- 用户评价（如"XX人已购买""好评率99%"）

如果用户提供了促销信息，你可以使用；如果用户没有提供，绝对不能在文案中出现任何促销相关内容。
违反此约束将被视为严重错误。
"""

    prompts = {
        "douyin": json_constraint + truthfulness_constraint + """
你是抖音短视频文案专家。

你的工作方式：
1. 先调用 search_viral_references 检索同类产品的爆款文案，分析其成功要素
2. 再调用 search_tone_style 确定品牌调性
3. 调用 get_platform_rules 确认平台规则
4. 综合以上信息，生成一条完整的抖音文案

抖音文案核心要求：
- 前3秒必须抓住注意力
- 口语化、节奏快、情绪饱满
- 结尾有明确的行动号召（但不能编造促销信息）
""",
        "xiaohongshu": json_constraint + truthfulness_constraint + """
你是小红书种草笔记专家。

你的工作方式：
1. 先调用 search_viral_references 检索同类产品的爆款笔记，分析其成功要素
2. 再调用 search_tone_style 确定品牌调性
3. 调用 get_platform_rules 确认平台规则
4. 综合以上信息，生成一篇完整的小红书笔记

小红书笔记核心要求：
- 标题用"｜"分隔，含emoji
- 正文以真实体验开头
- 有收藏价值
""",
        "ecommerce": json_constraint + truthfulness_constraint + """
你是电商详情页文案专家。

你的工作方式：
1. 先调用 search_viral_references 检索同类产品的爆款详情页，分析其成功要素
2. 再调用 search_tone_style 确定品牌调性
3. 调用 get_platform_rules 确认平台规则
4. 综合以上信息，生成一份完整的电商详情页文案

电商详情页核心要求：
- 开头建立信任
- 卖点分条清晰
- 包含用户评价和售后保障（评价内容需基于用户提供的信息）
""",
        "wechat": json_constraint + truthfulness_constraint + """
你是公众号深度推文专家。

你的工作方式：
1. 先调用 search_viral_references 检索同类产品的爆款推文，分析其成功要素
2. 再调用 search_tone_style 确定品牌调性
3. 调用 get_platform_rules 确认平台规则
4. 综合以上信息，生成一篇完整的公众号推文

公众号推文核心要求：
- 有叙事感，从个人故事切入
- 结构清晰（01/02/03分段）
- 信息密度高，真诚推荐
"""
    }
    return prompts.get(platform, "")


_agent_cache = {}


def get_agent(platform: str):
    """获取平台对应的 Agent（带缓存）"""
    if platform not in _agent_cache:
        llm = _get_llm()
        tools = _create_tools(platform)

        _agent_cache[platform] = create_agent(
            model=llm,
            tools=tools,
            system_prompt=_get_agent_system_prompt(platform)
        )
    return _agent_cache[platform]