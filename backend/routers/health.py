"""
健康检查路由
提供系统健康状态查询接口
"""
from fastapi import APIRouter
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["系统"]
)


# ==================== 路由处理器 ====================

@router.get("/")
async def root() -> Dict[str, Any]:
    """
    API 信息

    返回 API 的基本信息和可用接口列表
    """
    return {
        "name": "万物有灵 API",
        "version": "3.0.0",
        "description": "智能对话服务 - 提供天气查询、心情分析、智能对话等功能",
        "features": {
            "weather": "天气查询",
            "emotion": "心情分析",
            "chat_streaming": "流式智能对话"
        },
        "endpoints": {
            "GET /": "API信息",
            "GET /health": "健康检查",
            "POST /api/weather": "查询天气",
            "POST /api/emotion": "分析心情",
            "POST /api/chat/stream": "流式智能对话",
            "POST /api/chat/": "非流式智能对话"
        },
        "docs": "/docs"
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    健康检查

    返回各服务的运行状态
    """
    from main import weather_service, emotion_service, modelscope_service, supabase_service

    return {
        "status": "ok",
        "services": {
            "weather": weather_service is not None,
            "emotion": emotion_service is not None,
            "modelscope": modelscope_service is not None,
            "database": supabase_service is not None
        }
    }
