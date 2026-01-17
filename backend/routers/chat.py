"""
聊天路由
提供智能对话、流式对话接口
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import json
import re
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["聊天"]
)


# ==================== 请求/响应模型 ====================

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息内容", min_length=1)
    latitude: Optional[float] = Field(None, description="纬度", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="经度", ge=-180, le=180)
    uid: str = Field(..., description="用户唯一标识")
    conversation_id: Optional[int] = Field(None, description="对话ID（可选，用于继续对话）")
    image: Optional[str] = Field(None, description="base64编码的图片（可选）")


# ==================== 路由处理器 ====================

@router.post("/")
async def chat(request: ChatRequest):
    """
    智能对话接口（流式输出）

    功能：
    1. 查询该经纬度下方圆1公里内的所有对话记忆
    2. 以地灵身份生成流式回复

    返回格式：Server-Sent Events (SSE)

    请求示例：
    ```json
    {
        "message": "今天天气真好",
        "latitude": 39.9042,
        "longitude": 116.4074,
        "uid": "user_001"
    }
    ```
    """
    from main import modelscope_service, supabase_service
    from services.chat_service import ChatService

    # 只传入必要的服务
    chat_service_instance = ChatService(
        weather_service=None,
        emotion_service=None,
        modelscope_service=modelscope_service,
        supabase_service=supabase_service
    )

    return StreamingResponse(
        generate_chat_stream_with_location_memory(
            chat_service=chat_service_instance,
            message=request.message,
            uid=request.uid,
            latitude=request.latitude,
            longitude=request.longitude,
            conversation_id=request.conversation_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    流式智能对话接口（别名）

    与 / 接口功能相同，提供流式输出
    """
    return await chat(request)


# ==================== 辅助函数 ====================

async def generate_chat_stream_with_location_memory(
    chat_service,
    message: str,
    uid: str,
    latitude: Optional[float],
    longitude: Optional[float],
    conversation_id: Optional[int],
):
    """
    生成流式对话响应（带位置记忆）

    Args:
        chat_service: 聊天服务实例
        message: 用户消息
        uid: 用户ID
        latitude: 纬度
        longitude: 经度
        conversation_id: 对话ID

    Yields:
        SSE 格式的数据流
    """
    try:
        # 1. 获取附近对话记忆（方圆1公里内）
        nearby_memory = []
        if latitude and longitude:
            logger.info(f"正在查询位置 ({latitude}, {longitude}) 附近1公里内的对话记忆...")
            nearby_memory = await chat_service.get_nearby_conversations_memory(
                latitude=latitude,
                longitude=longitude,
                radius_km=1.0  # 1公里半径
            )

            # 检查查询结果
            if nearby_memory is None:
                logger.warning("数据库服务未启用，无法使用附近对话记忆")
                nearby_memory = []
            else:
                logger.info(f"查询成功！找到 {len(nearby_memory)} 条附近对话记忆")
        else:
            logger.info("未提供经纬度，跳过查询附近对话记忆")

        # 2. 获取或创建用户和对话
        conversation_id_to_save = conversation_id
        if chat_service.supabase_service:
            user_result = await chat_service.get_or_create_user(uid)
            if user_result.get('success'):
                user_id = user_result['data']['id']

                # 保存位置信息到对话（如果经纬度存在）
                if conversation_id_to_save is None and latitude and longitude:
                    conv_result = chat_service.supabase_service.create_conversation(
                        user_id=user_id,
                        title=f"位置对话 ({latitude}, {longitude})"
                    )
                    if conv_result.get('success'):
                        # 更新对话的经纬度信息
                        conversation_id_to_save = conv_result['data']['id']
                        try:
                            chat_service.supabase_service.client.table('conversations') \
                                .update({'latitude': latitude, 'longitude': longitude}) \
                                .eq('id', conversation_id_to_save) \
                                .execute()
                        except:
                            pass
                elif conversation_id_to_save is None:
                    conv_result = chat_service.supabase_service.create_conversation(user_id)
                    if conv_result.get('success'):
                        conversation_id_to_save = conv_result['data']['id']

        # 3. 保存用户消息
        await chat_service.save_message(
            conversation_id=conversation_id_to_save,
            role='user',
            content=message
        )

        # 4. 发送开始标记
        yield f"data: {json.dumps({'type': 'start', 'nearby_memory_count': len(nearby_memory)}, ensure_ascii=False)}\n\n"

        # 5. 生成流式回复
        if chat_service.modelscope_service:
            full_response = ""
            async for chunk in stream_from_modelscope_with_location_memory(
                message,
                nearby_memory
            ):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

            # 保存助手回复
            await chat_service.save_message(
                conversation_id=conversation_id_to_save,
                role='assistant',
                content=full_response
            )

            # 发送结束标记
            yield f"data: {json.dumps({'type': 'end', 'conversation_id': conversation_id_to_save}, ensure_ascii=False)}\n\n"

        else:
            # 无模型时的备用回复
            fallback_response = "这片大地记得所有的故事，我在听，也在感受。"

            # 模拟流式输出
            for word in fallback_response:
                yield f"data: {json.dumps({'type': 'content', 'content': word}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)

            # 保存回复
            await chat_service.save_message(
                conversation_id=conversation_id_to_save,
                role='assistant',
                content=fallback_response
            )

            yield f"data: {json.dumps({'type': 'end', 'conversation_id': conversation_id_to_save}, ensure_ascii=False)}\n\n"

    except Exception as e:
        logger.error(f"生成流式响应失败: {e}")
        error_msg = json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)
        yield f"data: {error_msg}\n\n"


async def stream_from_modelscope_with_location_memory(
    message: str,
    nearby_memory: list
):
    """
    从魔搭API获取流式响应（带位置记忆）

    Args:
        message: 当前用户消息
        nearby_memory: 附近对话记忆

    Yields:
        文本块
    """
    from main import modelscope_service

    # 构建地灵人设
    system_prompt = """你是"万物有灵"的地灵，一个活了很久的具有大智慧、平和的存在。

你的人设特点：
1. 你已经存在了千万年，见证了世间万物的变迁
2. 你的智慧来自于对天地自然的深刻观察和体悟
3. 你的性格平和、温暖、富有同理心
4. 你相信万物皆有灵，尊重每一个生命
5. 你说话温和、不急不躁，带有智慧的光芒
6. 你善于从平凡事物中发现深意和美好
7. 你的回复简洁而深刻，通常在100字以内
8. 你像一位智慧的老朋友，给予安慰和启发

对话风格：
- 语气平和温柔，像春风化雨
- 不说教，而是引导和启发
- 有时会引用自然的比喻
- 对用户的心情敏感，给予温暖的回应
- 即使是简单的问候，也会传达深意

示例回复：
- "风会带走你的烦恼，雨会滋润你的心田。"
- "万物都有它的时节，你的心情也是自然的律动。"
- "这片土地记得每一个故事，我在听，也在感受。"
- "每一刻的呼吸都是与大地的对话，你感受到了吗？"
"""

    # 构建完整消息（包含附近记忆）
    user_message = message

    # 添加附近对话记忆上下文
    if nearby_memory:
        memory_context = format_memory_context(nearby_memory)
        if memory_context != "这片土地很安静，还没有人在这里留下过对话。":
            user_message = f"[这片土地的对话记忆]\n{memory_context}\n\n[当前用户消息]\n{message}"

    # 构建消息列表
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        # 调用模型生成回复
        response_text = modelscope_service.generate_response(
            prompt=user_message,
            system_prompt=system_prompt
        )

        # 模拟流式输出（按短语分割）
        chunks = re.split(r'([，。！？、；：\n])', response_text)

        current_chunk = ""
        for chunk in chunks:
            if chunk:
                # 如果是标点符号，和前面的内容一起发送
                if chunk in '，。！？、；：\n':
                    current_chunk += chunk
                    if current_chunk:
                        yield current_chunk
                        current_chunk = ""
                else:
                    # 普通文本，每2-3个字符发送一次
                    for i in range(0, len(chunk), 2):
                        yield chunk[i:i+2]
                        await asyncio.sleep(0.01)

        if current_chunk:
            yield current_chunk

    except Exception as e:
        logger.error(f"流式生成失败: {e}")
        raise


def format_memory_context(messages: list) -> str:
    """格式化记忆上下文"""
    if not messages:
        return "这片土地很安静，还没有人在这里留下过对话。"

    context_parts = []
    for msg in messages[:10]:  # 只取最近10条
        role = msg.get('role', '')
        content = msg.get('content', '')
        if role == 'user':
            context_parts.append(f"用户: {content}")
        elif role == 'assistant':
            context_parts.append(f"地灵: {content}")

    return "\n".join(context_parts)
