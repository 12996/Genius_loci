"""
心情路由
提供心情分析接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/emotion",
    tags=["心情"]
)


# ==================== 请求/响应模型 ====================

class EmotionRequest(BaseModel):
    """心情分析请求模型"""
    text: str = Field(..., description="待分析的文本", min_length=1)


# ==================== 路由处理器 ====================

@router.post("")
async def analyze_emotion(request: EmotionRequest):
    """
    心情分析接口

    分析文本中的用户心情

    请求示例：
    ```json
    {
        "text": "我今天很开心"
    }
    ```

    返回示例：
    ```json
    {
        "success": true,
        "primary_emotion": "happy",
        "description": "心情愉悦",
        "emoji": "😊"
    }
    ```
    """
    from main import emotion_service, modelscope_service

    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="文本内容为空")

        print(modelscope_service)
        # 如果有魔搭服务，使用大模型分析；否则使用关键词分析
        if modelscope_service:
            result = emotion_service.analyze_with_llm(request.text, modelscope_service)
        else:
            result = emotion_service.analyze_emotion(request.text)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"心情分析错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
