import os
from dotenv import load_dotenv

# 加载本地的 .env 文件（如果存在）
load_dotenv()


class Settings:
    # 你的 API Key。可以是 OpenAI 的，也可以是阿里云 DashScope (兼容 OpenAI 协议)
    # 实际上为了演示，我们先预留在这里
    API_KEY = os.getenv("AI_API_KEY", "sk-placeholder")

    # AI 模型名称，例如 "qwen-turbo" (通义千问) 或 "gpt-3.5-turbo"
    MODEL_NAME = os.getenv("AI_MODEL_NAME", "gpt-3.5-turbo")

    # 模拟模式：如果没有 API Key，开启此模式返回假数据，方便你测试前端交互
    MOCK_MODE = True


settings = Settings()