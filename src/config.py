# src/config.py

import os
from dotenv import load_dotenv

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v2")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
VECTOR_DIR = os.path.join(BASE_DIR, "data", "vectors")

TOP_K_RETRIEVAL = 5
SIMILARITY_THRESHOLD = 0.5

PLATFORMS = ["douyin", "xiaohongshu", "ecommerce", "wechat"]