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


class ChatResponse(BaseModel):
    """聊天响应模型"""
    success: bool
    response: Optional[str] = None
    conversation_id: Optional[int] = None
    emotion_analysis: Optional[Dict[str, Any]] = None
    weather_info: Optional[str] = None
    image_info: Optional[str] = None


# ==================== 路由处理器 ====================

@router.post("/stream", response_class=StreamingResponse)
async def chat_streaming(request: ChatRequest):
    """
    流式智能对话接口（主要接口）

    功能：
    1. 根据经纬度查询天气
    2. 分析用户消息中的心情
    3. 获取用户在当前位置的对话记忆
    4. 以地灵身份生成流式回复

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
    from main import weather_service, emotion_service, modelscope_service, supabase_service
    from services.chat_service import ChatService

    # 创建聊天服务实例
    chat_service = ChatService(weather_service, emotion_service, modelscope_service, supabase_service)

    return StreamingResponse(
        generate_chat_stream(
            message=request.message,
            uid=request.uid,
            latitude=request.latitude,
            longitude=request.longitude,
            conversation_id=request.conversation_id,
            image=request.image
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/")
async def chat(request: ChatRequest):
    """
    智能对话接口（流式输出）

    功能：
    1. 根据经纬度查询天气
    2. 分析用户消息中的心情
    3. 查询该经纬度下方圆1公里内的所有对话记忆
    4. 以地灵身份生成流式回复

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
    from main import weather_service, emotion_service, modelscope_service, supabase_service
    from services.chat_service import ChatService

    chat_service_instance = ChatService(weather_service, emotion_service, modelscope_service, supabase_service)

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
        # 1. 分析心情
        emotion_analysis = chat_service.analyze_emotion(message)
        emotion_summary = chat_service.emotion_service.get_emotion_summary(message)

        # 2. 获取天气
        weather_info = None
        weather_data_dict = None
        if latitude and longitude:
            weather_data = chat_service.weather_service.get_weather_by_coords(latitude, longitude)
            if weather_data.get('success'):
                weather_info = chat_service.weather_service.get_weather_summary(latitude, longitude)
                weather_data_dict = weather_data

        # 3. 获取附近对话记忆（方圆1公里内）
        nearby_memory = []
        if latitude and longitude:
            nearby_memory = await chat_service.get_nearby_conversations_memory(
                latitude=latitude,
                longitude=longitude,
                radius_km=1.0  # 1公里半径
            )

        # 4. 获取或创建用户和对话
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

        # 5. 保存用户消息
        await chat_service.save_message(
            conversation_id=conversation_id_to_save,
            role='user',
            content=message,
            emotion_data=emotion_analysis,
            weather_data=weather_data_dict
        )

        # 6. 发送开始标记
        yield f"data: {json.dumps({'type': 'start', 'emotion_analysis': emotion_analysis, 'weather_info': weather_info, 'nearby_memory_count': len(nearby_memory)}, ensure_ascii=False)}\n\n"

        # 7. 生成流式回复
        if chat_service.modelscope_service:
            full_response = ""
            async for chunk in stream_from_modelscope_with_location_memory(
                message,
                nearby_memory,
                weather_info,
                emotion_summary
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
            fallback_response = chat_service.generate_fallback_response(message, emotion_summary, weather_info)

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
    nearby_memory: list,
    weather_info: Optional[str],
    emotion_info: Optional[str]
):
    """
    从魔搭API获取流式响应（带位置记忆）

    Args:
        message: 当前用户消息
        nearby_memory: 附近对话记忆
        weather_info: 天气信息
        emotion_info: 心情信息

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

    # 添加天气信息
    if weather_info:
        user_message = f"[当前天气: {weather_info}]\n\n{user_message}"

    # 添加心情信息
    if emotion_info:
        user_message = f"[用户心情: {emotion_info}]\n\n{user_message}"

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


    try:
        # 1. 分析心情
        emotion_analysis = emotion_service.analyze_emotion(request.message)
        emotion_summary = emotion_service.get_emotion_summary(request.message)

        # 2. 获取天气
        weather_info = None
        weather_data_dict = None
        if request.latitude and request.longitude:
            weather_data = weather_service.get_weather_by_coords(request.latitude, request.longitude)
            if weather_data.get('success'):
                weather_info = weather_service.get_weather_summary(request.latitude, request.longitude)
                weather_data_dict = weather_data

        # 3. 获取对话记忆
        memory_messages = await get_conversation_memory(request.uid, request.conversation_id)

        # 4. 获取或创建用户和对话
        user_result = await get_or_create_user(request.uid)
        conversation_id_to_save = request.conversation_id
        if user_result.get('success') and supabase_service:
            user_id = user_result['data']['id']
            if conversation_id_to_save is None:
                conv_result = supabase_service.create_conversation(user_id)
                if conv_result.get('success'):
                    conversation_id_to_save = conv_result['data']['id']

        # 5. 保存用户消息
        await save_message(
            conversation_id=conversation_id_to_save,
            role='user',
            content=request.message,
            emotion_data=emotion_analysis,
            weather_data=weather_data_dict
        )

        # 6. 生成回复
        if modelscope_service:
            response_text = await generate_response_with_memory(
                request.message,
                memory_messages,
                weather_info,
                emotion_summary
            )
        else:
            response_text = generate_simple_response(request.message, emotion_summary, weather_info)

        # 7. 保存助手回复
        await save_message(
            conversation_id=conversation_id_to_save,
            role='assistant',
            content=response_text
        )

        return ChatResponse(
            success=True,
            response=response_text,
            conversation_id=conversation_id_to_save,
            emotion_analysis=emotion_analysis,
            weather_info=weather_info
        )

    except Exception as e:
        logger.error(f"对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 辅助函数 ====================

async def generate_chat_stream(
    message: str,
    uid: str,
    latitude: Optional[float],
    longitude: Optional[float],
    conversation_id: Optional[int],
    image: Optional[str]
):
    """
    生成流式对话响应

    Args:
        message: 用户消息
        uid: 用户ID
        latitude: 纬度
        longitude: 经度
        conversation_id: 对话ID
        image: base64图片

    Yields:
        SSE 格式的数据流
    """
    from main import weather_service, emotion_service, modelscope_service, supabase_service
    from services.chat_service import ChatService

    chat_service = ChatService(weather_service, emotion_service, modelscope_service, supabase_service)

    try:
        # 1. 分析心情
        emotion_analysis = emotion_service.analyze_emotion(message)
        emotion_summary = emotion_service.get_emotion_summary(message)

        # 2. 获取天气
        weather_info = None
        weather_data_dict = None
        if latitude and longitude:
            weather_data = weather_service.get_weather_by_coords(latitude, longitude)
            if weather_data.get('success'):
                weather_info = weather_service.get_weather_summary(latitude, longitude)
                weather_data_dict = weather_data

        # 3. 获取对话记忆
        memory_messages = await get_conversation_memory(uid, conversation_id)

        # 4. 获取或创建用户和对话
        conversation_id_to_save = conversation_id
        if supabase_service:
            user_result = await get_or_create_user(uid)
            if user_result.get('success'):
                user_id = user_result['data']['id']
                if conversation_id_to_save is None:
                    conv_result = supabase_service.create_conversation(user_id)
                    if conv_result.get('success'):
                        conversation_id_to_save = conv_result['data']['id']

        # 5. 保存用户消息
        await save_message(
            conversation_id=conversation_id_to_save,
            role='user',
            content=message,
            emotion_data=emotion_analysis,
            weather_data=weather_data_dict
        )

        # 6. 发送开始标记
        yield f"data: {json.dumps({'type': 'start', 'emotion_analysis': emotion_analysis, 'weather_info': weather_info}, ensure_ascii=False)}\n\n"

        # 7. 生成流式回复
        if modelscope_service:
            full_response = ""
            async for chunk in stream_from_modelscope_with_context(
                message,
                memory_messages,
                weather_info,
                emotion_summary
            ):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

            # 保存助手回复
            await save_message(
                conversation_id=conversation_id_to_save,
                role='assistant',
                content=full_response
            )

            # 发送结束标记
            yield f"data: {json.dumps({'type': 'end', 'conversation_id': conversation_id_to_save}, ensure_ascii=False)}\n\n"

        else:
            # 无模型时的备用回复
            fallback_response = generate_simple_response(message, emotion_summary, weather_info)

            # 模拟流式输出
            for word in fallback_response:
                yield f"data: {json.dumps({'type': 'content', 'content': word}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)

            # 保存回复
            await save_message(
                conversation_id=conversation_id_to_save,
                role='assistant',
                content=fallback_response
            )

            yield f"data: {json.dumps({'type': 'end', 'conversation_id': conversation_id_to_save}, ensure_ascii=False)}\n\n"

    except Exception as e:
        logger.error(f"生成流式响应失败: {e}")
        error_msg = json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)
        yield f"data: {error_msg}\n\n"


async def stream_from_modelscope_with_context(
    message: str,
    memory_messages: list,
    weather_info: Optional[str],
    emotion_info: Optional[str]
):
    """
    从魔搭API获取流式响应（带上下文和记忆）

    Args:
        message: 当前用户消息
        memory_messages: 历史对话记忆
        weather_info: 天气信息
        emotion_info: 心情信息

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

    # 构建完整消息（包含记忆）
    user_message = message

    # 添加历史对话上下文
    if memory_messages:
        memory_context = format_memory_context(memory_messages)
        if memory_context != "这是我们的第一次对话。":
            user_message = f"[之前的对话记忆]\n{memory_context}\n\n[当前用户消息]\n{message}"

    # 添加天气信息
    if weather_info:
        user_message = f"[当前天气: {weather_info}]\n\n{user_message}"

    # 添加心情信息
    if emotion_info:
        user_message = f"[用户心情: {emotion_info}]\n\n{user_message}"

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


async def generate_response_with_memory(
    message: str,
    memory_messages: list,
    weather_info: Optional[str],
    emotion_info: Optional[str]
) -> str:
    """
    生成回复（带记忆）
    """
    from main import modelscope_service

    system_prompt = """你是"万物有灵"的地灵，一个活了很久的具有大智慧、平和的存在。
你的回复温和、切生动形象，就想一位有智慧的老者。"""

    user_message = message

    if memory_messages:
        memory_context = format_memory_context(memory_messages)
        if memory_context != "这是我们的第一次对话。":
            user_message = f"[对话记忆]\n{memory_context}\n\n{message}"

    if weather_info:
        user_message = f"[天气: {weather_info}]\n\n{user_message}"

    if emotion_info:
        user_message = f"[心情: {emotion_info}]\n\n{user_message}"

    try:
        response = modelscope_service.generate_response(
            prompt=user_message,
            system_prompt=system_prompt
        )
        return response
    except Exception as e:
        logger.error(f"生成回复失败: {e}")
        return generate_simple_response(message, emotion_info, weather_info)


def format_memory_context(messages: list) -> str:
    """格式化记忆上下文"""
    if not messages:
        return "这是我们的第一次对话。"

    context_parts = []
    for msg in messages[:10]:  # 只取最近10条
        role = msg.get('role', '')
        content = msg.get('content', '')
        if role == 'user':
            context_parts.append(f"用户: {content}")
        elif role == 'assistant':
            context_parts.append(f"地灵: {content}")

    return "\n".join(context_parts)


def generate_simple_response(message: str, emotion_info: Optional[str], weather_info: Optional[str]) -> str:
    """生成简单回复（无模型时）"""
    responses = []

    if weather_info:
        responses.append(f"今天{weather_info}")

    if emotion_info:
        responses.append(f"，{emotion_info}")

    base_response = "".join(responses) if responses else "我在听"

    wisdom_responses = [
        "万物皆有灵性，你感受到了吗？",
        "风会带来消息，雨会滋润心田。",
        "每一刻都值得被铭记。",
        "继续和我说说吧，我在倾听。",
        "这片大地记得所有的故事。",
        "自然的韵律在呼吸间流动。",
    ]

    import random
    return base_response + "。" + random.choice(wisdom_responses)
