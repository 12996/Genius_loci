"""
天气路由
提供天气查询接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/weather",
    tags=["天气"]
)


# ==================== 请求/响应模型 ====================

class WeatherRequest(BaseModel):
    """天气请求模型"""
    latitude: float = Field(..., description="纬度", ge=-90, le=90)
    longitude: float = Field(..., description="经度", ge=-180, le=180)


# ==================== 路由处理器 ====================

@router.post("")
async def get_weather(request: WeatherRequest):
    """
    查询天气接口

    根据经纬度查询当前天气信息

    请求示例：
    ```json
    {
        "latitude": 39.9042,
        "longitude": 116.4074
    }
    ```

    返回示例：
    ```json
    {
        "success": true,
        "current": {
            "temperature": 25,
            "humidity": 60,
            "weather_description": "晴朗"
        }
    }
    ```
    """
    from main import weather_service

    try:
        result = weather_service.get_weather_by_coords(request.latitude, request.longitude)
        return result

    except Exception as e:
        logger.error(f"天气查询错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
