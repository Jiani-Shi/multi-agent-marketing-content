# src/retriever.py

from typing import Dict, List, Any, Optional
from .vector_store import (
    load_viral_vector_store,
    load_tone_vector_store,
    retrieve_viral_examples,
    retrieve_tone
)
from .config import TOP_K_RETRIEVAL


class DualRetriever:
    def __init__(self):
        print("正在加载向量库...")
        self.viral_store = load_viral_vector_store()
        self.tone_store = load_tone_vector_store()
        
        viral_status = "√" if self.viral_store else "x"
        tone_status = "√" if self.tone_store else "x"
        print(f"爆款库: {viral_status}  调性库: {tone_status}")
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = TOP_K_RETRIEVAL,
        selected_tone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        双路检索
        
        参数:
            query: 查询文本
            top_k: 爆款库返回数量
            selected_tone: 用户手动选择的调性名称，如果为 None 则自动匹配
        """
        # 路一：爆款库检索
        viral_examples = retrieve_viral_examples(self.viral_store, query, top_k)
        
        # 路二：调性检索（支持用户选择或自动匹配）
        if selected_tone:
            # 用户主动选择了调性 → 从调性库中精确查找该名称
            tone_style = self._get_tone_by_name(selected_tone)
        else:
            # 用户未选择 → 系统自动匹配
            tone_style = retrieve_tone(self.tone_store, query, top_k=1)
        
        return {
            "viral_examples": viral_examples,
            "tone_style": tone_style,
            "query": query,
            "selected_tone": selected_tone  # 记录用户是否选择了
        }
    
    def _get_tone_by_name(self, tone_name: str) -> Dict:
        """根据调性名称精确查找（而非向量检索）"""
        # 这里需要遍历调性库的元数据来匹配
        # 简单实现：直接从 tone_library.json 读取
        import json
        import os
        from .config import BASE_DIR
        
        tone_file = os.path.join(BASE_DIR, "data", "brand_tone", "tone_library.json")
        with open(tone_file, 'r', encoding='utf-8') as f:
            tone_data = json.load(f)
        
        if tone_name in tone_data:
            info = tone_data[tone_name]
            return {
                "tone_name": tone_name,
                "description": info.get("description", ""),
                "keywords": info.get("keywords", []),
                "tone": info.get("tone", ""),
                "score": 1.0,  # 用户手动选择，相似度设为满分
                "source": "user_selected"
            }
        else:
            # 如果用户输入的调性名称不存在，降级为自动匹配
            return retrieve_tone(self.tone_store, tone_name, top_k=1)


if __name__ == "__main__":
    retriever = DualRetriever()
    
    print("\n测试1：用户未选择调性（自动匹配）")
    result1 = retriever.retrieve("美白精华")
    print(f"匹配调性：{result1['tone_style'].get('tone_name', '未匹配')}")
    
    print("\n测试2：用户手动选择调性（'活力潮流风'）")
    result2 = retriever.retrieve("美白精华", selected_tone="活力潮流风")
    print(f"匹配调性：{result2['tone_style'].get('tone_name', '未匹配')}")
    print(f"来源：{result2['tone_style'].get('source', 'auto')}")