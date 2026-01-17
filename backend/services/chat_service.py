"""
聊天服务
封装对话相关的业务逻辑
"""
import logging
from typing import Optional, List, Dict, Any, AsyncGenerator

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务类"""

    def __init__(self, weather_service, emotion_service, modelscope_service, supabase_service):
        """
        初始化聊天服务

        Args:
            weather_service: 天气服务
            emotion_service: 心情服务
            modelscope_service: 模型服务
            supabase_service: 数据库服务
        """
        self.weather_service = weather_service
        self.emotion_service = emotion_service
        self.modelscope_service = modelscope_service
        self.supabase_service = supabase_service

    async def get_or_create_user(self, uid: str) -> Dict:
        """获取或创建用户"""
        if not self.supabase_service:
            return {'success': False, 'error': '数据库服务未启用'}

        try:
            result = self.supabase_service.get_or_create_user_by_device(uid)
            return result
        except Exception as e:
            logger.error(f"获取/创建用户失败: {e}")
            return {'success': False, 'error': str(e)}

    async def get_conversation_memory(self, uid: str, conversation_id: Optional[int] = None) -> List[Dict]:
        """获取对话记忆"""
        if not self.supabase_service:
            return []

        try:
            # 获取用户信息
            user_result = await self.get_or_create_user(uid)
            if not user_result.get('success'):
                return []

            user_id = user_result['data']['id']

            # 如果没有指定对话ID，获取最近的消息
            if conversation_id is None:
                # 获取用户最近的对话
                conv_result = self.supabase_service.get_conversations(user_id, limit=1)
                if conv_result.get('success') and conv_result.get('data'):
                    conversation_id = conv_result['data'][0]['id']
                else:
                    # 创建新对话
                    new_conv = self.supabase_service.create_conversation(user_id)
                    if new_conv.get('success'):
                        conversation_id = new_conv['data']['id']
                    else:
                        return []

            # 获取对话消息
            messages_result = self.supabase_service.get_recent_messages(conversation_id, count=20)
            if messages_result.get('success'):
                return messages_result.get('data', [])

            return []

        except Exception as e:
            logger.error(f"获取对话记忆失败: {e}")
            return []

    async def save_message(self, conversation_id: int, role: str, content: str,
                          emotion_data: Optional[Dict] = None,
                          weather_data: Optional[Dict] = None,
                          image_info: Optional[Dict] = None):
        """保存消息到数据库"""
        if not self.supabase_service:
            return

        try:
            self.supabase_service.add_message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                emotion_data=emotion_data,
                weather_data=weather_data,
                image_info=image_info
            )
        except Exception as e:
            logger.error(f"保存消息失败: {e}")

    def format_memory_context(self, messages: List[Dict]) -> str:
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

    def get_weather_info(self, latitude: float, longitude: float) -> Optional[Dict]:
        """获取天气信息"""
        if not latitude or not longitude:
            return None

        try:
            weather_data = self.weather_service.get_weather_by_coords(latitude, longitude)
            if weather_data.get('success'):
                return {
                    'summary': self.weather_service.get_weather_summary(latitude, longitude),
                    'detail': weather_data
                }
        except Exception as e:
            logger.error(f"获取天气信息失败: {e}")

        return None

    async def get_nearby_conversations_memory(self, latitude: float, longitude: float,
                                              radius_km: float = 1.0) -> List[Dict]:
        """
        获取指定位置附近的对话记忆

        Args:
            latitude: 纬度
            longitude: 经度
            radius_km: 半径（公里）

        Returns:
            附近的消息列表
        """
        if not self.supabase_service:
            logger.warning("数据库服务未启用，无法查询附近对话记忆")
            return None

        try:
            logger.info(f"调用数据库服务查询附近对话: lat={latitude}, lon={longitude}, radius={radius_km}km")
            result = self.supabase_service.get_nearby_conversations(
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                limit=50
            )

            if result.get('success'):
                memory_count = len(result.get('data', []))
                logger.info(f"数据库查询成功，返回 {memory_count} 条对话记忆")
                return result.get('data', [])
            else:
                logger.error(f"数据库查询失败: {result.get('error', '未知错误')}")
                return []

        except Exception as e:
            logger.error(f"获取附近对话记忆异常: {e}", exc_info=True)
            return []

    def analyze_emotion(self, text: str) -> Dict:
        """分析心情"""
        try:
            return self.emotion_service.analyze_emotion(text)
        except Exception as e:
            logger.error(f"分析心情失败: {e}")
            return {'success': False, 'error': str(e)}

    def generate_fallback_response(self, message: str, emotion_summary: Optional[str],
                                  weather_info: Optional[str]) -> str:
        """生成备用回复（无模型服务时）"""
        responses = []

        if weather_info:
            responses.append(f"今天{weather_info}")

        if emotion_summary:
            responses.append(f"，{emotion_summary}")

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
