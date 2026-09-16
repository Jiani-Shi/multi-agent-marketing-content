# src/prompts/__init__.py

from .base import BasePrompt
from .douyin import DouyinPrompt
from .xiaohongshu import XiaohongshuPrompt
from .ecommerce import EcommercePrompt
from .wechat import WechatPrompt

PROMPT_MAP = {
    "douyin": DouyinPrompt,
    "xiaohongshu": XiaohongshuPrompt,
    "ecommerce": EcommercePrompt,
    "wechat": WechatPrompt,
}


def get_prompt_loader(platform: str):
    """根据平台名称获取对应的 Prompt 加载器类"""
    if platform not in PROMPT_MAP:
        raise ValueError(f"不支持的平台: {platform}，可选: {list(PROMPT_MAP.keys())}")
    return PROMPT_MAP[platform]


def list_platforms():
    """返回所有支持的平台列表"""
    return list(PROMPT_MAP.keys())