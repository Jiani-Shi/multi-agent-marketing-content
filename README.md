# 跨平台智能营销内容生成系统

针对多平台营销文案生成依赖人工、效率低且风格不统一的问题，构建了一个 AI 内容生成工具。输入产品名称与核心卖点，自动生成适配抖音、小红书、电商、公众号四个平台的结构化营销文案。


## 效果展示

![界面截图](docs/images/demo_interface.png)

![生成结果](docs/images/demo_result.png)


## 系统架构

![架构图](docs/images/architecture.png)

系统核心流程：

1. 用户输入产品信息，选择目标平台和品牌调性
2. 双路 RAG 检索：路一从爆款素材库检索相似文案，路二从品牌调性库检索风格约束
3. 各平台 Agent 自主调用工具，综合检索结果和平台规则生成文案
4. 四层兜底解析确保 JSON 格式稳定，前端展示结构化结果


## 技术栈

| 层次 | 技术选型 |
|------|----------|
| 编程语言 | Python 3.10 |
| Agent 框架 | LangChain |
| 大语言模型 | 通义千问 qwen-plus |
| 向量化模型 | text-embedding-v2 |
| 向量数据库 | FAISS |
| 前端框架 | Gradio |


## 核心功能

- 多 Agent 协作架构：为四个平台分别设计独立 Agent，每个 Agent 配备爆款检索、调性匹配、平台规则查询三类工具
- 双路 RAG 检索增强：路一提供爆款参考（写什么），路二提供风格约束（怎么写）
- 分层 Prompt 工程：包含 JSON 格式约束、信息真实性约束、平台规则、负面约束、思维链引导
- 四层兜底解析：直接解析、提取花括号、正则匹配、原文兜底，确保系统不会因格式问题崩溃


## 快速开始

### 1. 克隆项目

git clone https://github.com/your-username/marketing-content-generator.git
cd marketing-content-generator

### 2. 创建虚拟环境

python -m venv marketing_env
source marketing_env/bin/activate

Windows 用户使用：marketing_env\Scripts\activate

### 3. 安装依赖

pip install -r requirements.txt

### 4. 配置 API Key

在项目根目录创建 .env 文件：

DASHSCOPE_API_KEY=sk-你的通义千问密钥
LLM_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v2

### 5. 构建向量库

python -m src.vector_store

### 6. 启动应用

python app.py

浏览器打开 http://127.0.0.1:7860 即可使用。


## 项目结构

Marketing Content Generator/
├── data/
│   ├── raw/                        爆款素材库
│   ├── brand_tone/                 品牌调性库
│   └── vectors/                    FAISS 索引（代码生成）
├── src/
│   ├── config.py                   全局配置
│   ├── vector_store.py             向量库构建与检索
│   ├── retriever.py                双路 RAG 检索器
│   ├── router.py                   Agent 路由与构建
│   ├── generator.py                生成引擎
│   └── prompts/                    各平台 Prompt 模板
├── docs/
│   └── images/                     文档图片
├── app.py                          Gradio 前端入口
├── requirements.txt
└── README.md


## 实验结果

- 50 次生成测试中，JSON 解析成功率 100%
- 单平台平均生成耗时 8.3 秒，四平台批量生成约 10 秒
- 输出字数符合各平台特征：抖音约 139 字，小红书约 247 字，电商约 358 字，公众号约 359 字


## 开发环境

普通 CPU 笔记本即可完成全部开发与演示，无需 GPU。
