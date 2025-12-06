import os
from dotenv import load_dotenv

# 加载本地的 .env 文件（如果存在）
load_dotenv()


class Settings:
    # 从环境变量获取 Key，如果没获取到，默认为空
    API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

    # 阿里云百炼的兼容 OpenAI 调用地址
    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # 使用通义千问模型 (qwen-plus 效果好，qwen-turbo 速度快且便宜)
    MODEL_NAME = "qwen-plus"

    # 模拟模式：如果没有 API Key，开启此模式返回假数据，方便你测试前端交互
    MOCK_MODE = False

    # Redis 配置 (从环境变量取)
    # 格式示例: redis://default:你的密码@你的地址.upstash.io:6379
    REDIS_URL = os.getenv("REDIS_URL", "")


settings = Settings()
