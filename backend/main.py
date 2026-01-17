"""
万物有灵 - FastAPI 主应用
提供智能对话、天气查询、心情分析等功能
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from config import config
from services import WeatherService, EmotionService, ModelScopeService, SupabaseService, ChatService
from routers import chat_router, weather_router, emotion_router, health_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== 全局服务实例 ====================

weather_service = None
emotion_service = None
modelscope_service = None
supabase_service = None
chat_service = None


# ==================== Lifespan 事件处理器 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global weather_service, emotion_service, modelscope_service, supabase_service, chat_service

    # 启动时初始化服务
    logger.info("正在初始化服务...")

    # 基础服务
    weather_service = WeatherService()
    emotion_service = EmotionService()
    logger.info("✓ 基础服务已初始化")

    # 获取配置
    env = os.getenv('ENV', 'development')
    cfg = config[env]

    # 魔搭AI服务
    if cfg.MODELSCOPE_API_KEY:
        try:
            modelscope_service = ModelScopeService(cfg.MODELSCOPE_API_KEY)
            logger.info("✓ 魔搭AI服务已初始化")
        except Exception as e:
            logger.error(f"✗ 魔搭AI服务初始化失败: {e}")
    else:
        logger.warning("⚠ 未配置魔搭API key，智能对话功能将受限")

    # 数据库服务
    if cfg.SUPABASE_URL and cfg.SUPABASE_KEY:
        try:
            supabase_service = SupabaseService(cfg.SUPABASE_URL, cfg.SUPABASE_KEY)
            logger.info("✓ Supabase数据库服务已初始化")
        except Exception as e:
            logger.error(f"✗ Supabase初始化失败: {e}")
            supabase_service = None
    else:
        logger.warning("⚠ 未配置数据库，对话记忆功能将不可用")
        supabase_service = None

    # 聊天服务
    chat_service = ChatService(weather_service, emotion_service, modelscope_service, supabase_service)
    logger.info("✓ 聊天服务已初始化")

    logger.info("=" * 50)
    logger.info(f"环境: {env}")
    logger.info(f"调试模式: {cfg.DEBUG}")
    logger.info(f"魔搭AI: {'已启用' if modelscope_service else '未启用'}")
    logger.info(f"数据库: {'已连接' if supabase_service else '未连接'}")
    logger.info("=" * 50)

    yield

    # 关闭时的清理工作
    logger.info("服务关闭")


# ==================== 创建 FastAPI 应用 ====================

app = FastAPI(
    title="万物有灵 API",
    description="智能对话服务 - 提供天气查询、心情分析、智能对话等功能",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== 配置 CORS ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 注册路由 ====================

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(weather_router)
app.include_router(emotion_router)


# ==================== 主程序 ====================

if __name__ == "__main__":
    import uvicorn

    # 获取配置
    env = os.getenv('ENV', 'development')
    cfg = config[env]

    port = cfg.PORT
    debug = cfg.DEBUG

    # 打印启动信息
    print("=" * 60)
    print("万物有灵后端服务器 v3.0 (FastAPI)")
    print("=" * 60)
    print(f"环境: {env}")
    print(f"调试模式: {debug}")
    print(f"端口: {port}")
    print("\n功能状态:")
    print("  ✓ 天气查询服务")
    print("  ✓ 心情分析服务")
    print("  ✓ 流式智能对话")
    if cfg.MODELSCOPE_API_KEY:
        print("  ✓ 魔搭AI服务")
    else:
        print("  ⚠ 魔搭AI服务（未配置API key）")
    if cfg.SUPABASE_URL and cfg.SUPABASE_KEY:
        print("  ✓ 数据库服务")
    else:
        print("  ⚠ 数据库服务（未配置）")
    print("\nAPI接口:")
    print("  - GET  /                 : API信息")
    print("  - GET  /health           : 健康检查")
    print("  - POST /api/weather      : 天气查询")
    print("  - POST /api/emotion      : 心情分析")
    print("  - POST /api/chat/        : 智能对话（流式+位置记忆）")
    print("  - POST /api/chat/stream  : 智能对话（流式）")
    print(f"\n服务器地址: http://localhost:{port}")
    print(f"API文档: http://localhost:{port}/docs")
    print("=" * 60)
    print()

    # 启动服务器
    if debug:
        # 开发模式：使用 reload，需要传递字符串
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="info",
            access_log=True
        )
    else:
        # 生产模式：直接传递 app 对象
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
