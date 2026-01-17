"""
配置文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置"""

    # 环境配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    ENV = os.getenv('ENV', 'development')
    DEBUG = ENV == 'development'

    # 服务器配置
    PORT = int(os.getenv('PORT', 8000))

    # 魔搭API配置
    MODELSCOPE_API_KEY = os.getenv('MODELSCOPE_API_KEY', '')
    MODELSCOPE_API_BASE = "https://api-inference.modelscope.cn/v1"

    # 默认使用的模型（可通过环境变量覆盖）
    # 可选模型列表：
    # - qwen/Qwen2.5-7B-Instruct (推荐，性价比高)
    # - Qwen/Qwen2.5-72B-Instruct (更强大但较慢)
    # - qwen/Qwen2-7B-Instruct (旧版本)
    # - TAICHI/scenario_llm3.0_7b (场景对话模型)
    DEFAULT_MODEL = os.getenv('MODELSCOPE_MODEL', 'qwen/Qwen2.5-7B-Instruct')

    # Supabase配置
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

    # 天气API配置 (Open-Meteo)
    WEATHER_API_BASE = "https://api.open-meteo.com/v1"

    # 图片处理配置
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

    # CORS配置
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5000", "http://127.0.0.1:5000"]

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
