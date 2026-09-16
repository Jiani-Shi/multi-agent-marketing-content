# src/vector_store.py

import json
import os
import pickle
from typing import List, Dict, Any

import faiss
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from .config import (
    DASHSCOPE_API_KEY,
    EMBEDDING_MODEL,
    RAW_DATA_DIR,
    VECTOR_DIR,
    TOP_K_RETRIEVAL
)

embeddings = DashScopeEmbeddings(
    model=EMBEDDING_MODEL,
    dashscope_api_key=DASHSCOPE_API_KEY
)


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_viral_vector_store():
    print("构建爆款素材向量库...")
    
    all_documents = []
    
    for filename in os.listdir(RAW_DATA_DIR):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(RAW_DATA_DIR, filename)
        data = load_json_data(filepath)
        platform = filename.replace('_samples.json', '')
        
        for item in data:
            text_content = f"{item.get('title', '')}\n{item.get('content', '')}"
            
            doc = Document(
                page_content=text_content,
                metadata={
                    "platform": item.get("platform", platform),
                    "category": item.get("category", ""),
                    "title": item.get("title", ""),
                    "tags": item.get("tags", []),
                    "likes": item.get("likes", 0),
                    "raw_data": item
                }
            )
            all_documents.append(doc)
    
    print(f"共加载 {len(all_documents)} 条爆款文案")
    
    vector_store = FAISS.from_documents(all_documents, embeddings)
    
    save_path = os.path.join(VECTOR_DIR, "viral_index")
    vector_store.save_local(save_path)
    print(f"√ 爆款向量库已保存至: {save_path}")
    
    return vector_store


def build_tone_vector_store():
    print("构建品牌调性向量库...")
    
    tone_file = os.path.join(os.path.dirname(RAW_DATA_DIR), "brand_tone", "tone_library.json")
    
    if not os.path.exists(tone_file):
        print("品牌调性文件不存在，跳过构建")
        return None
    
    with open(tone_file, 'r', encoding='utf-8') as f:
        tone_data = json.load(f)
    
    documents = []
    
    for tone_name, tone_info in tone_data.items():
        text_content = f"""
调性名称：{tone_name}
描述：{tone_info.get('description', '')}
关键词：{', '.join(tone_info.get('keywords', []))}
语气：{tone_info.get('tone', '')}
        """
        
        doc = Document(
            page_content=text_content.strip(),
            metadata={
                "tone_name": tone_name,
                "description": tone_info.get("description", ""),
                "keywords": tone_info.get("keywords", []),
                "tone": tone_info.get("tone", "")
            }
        )
        documents.append(doc)
    
    print(f"共加载 {len(documents)} 种品牌调性")
    
    vector_store = FAISS.from_documents(documents, embeddings)
    
    save_path = os.path.join(VECTOR_DIR, "tone_index")
    vector_store.save_local(save_path)
    print(f"√ 调性向量库已保存至: {save_path}")
    
    return vector_store


def load_viral_vector_store():
    load_path = os.path.join(VECTOR_DIR, "viral_index")
    if os.path.exists(load_path):
        return FAISS.load_local(load_path, embeddings, allow_dangerous_deserialization=True)
    return None


def load_tone_vector_store():
    load_path = os.path.join(VECTOR_DIR, "tone_index")
    if os.path.exists(load_path):
        return FAISS.load_local(load_path, embeddings, allow_dangerous_deserialization=True)
    return None


def retrieve_viral_examples(vector_store, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[Dict]:
    if vector_store is None:
        return []
    
    results = vector_store.similarity_search_with_score(query, k=top_k)
    
    retrieved = []
    for doc, score in results:
        retrieved.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score)
        })
    
    return retrieved


def retrieve_tone(vector_store, query: str, top_k: int = 1) -> Dict:
    if vector_store is None:
        return {}
    
    results = vector_store.similarity_search_with_score(query, k=top_k)
    
    if results:
        doc, score = results[0]
        return {
            "tone_name": doc.metadata.get("tone_name", ""),
            "description": doc.metadata.get("description", ""),
            "keywords": doc.metadata.get("keywords", []),
            "tone": doc.metadata.get("tone", ""),
            "score": float(score)
        }
    
    return {}


if __name__ == "__main__":
    os.makedirs(VECTOR_DIR, exist_ok=True)
    
    build_viral_vector_store()
    build_tone_vector_store()
    
    print("√ 所有向量库构建完成")