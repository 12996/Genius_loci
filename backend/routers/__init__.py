"""
路由模块
"""
from .chat import router as chat_router
from .weather import router as weather_router
from .emotion import router as emotion_router
from .health import router as health_router

__all__ = ['chat_router', 'weather_router', 'emotion_router', 'health_router']
