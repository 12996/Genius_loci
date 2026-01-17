"""
Supabase数据库服务
提供数据库操作的统一接口层
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseService:
    """Supabase数据库服务类"""

    def __init__(self, url: str, key: str):
        """
        初始化Supabase客户端

        参数:
            url: Supabase项目URL
            key: Supabase API key
        """
        self.url = url
        self.key = key
        self.client: Optional[Client] = None

        try:
            self.client = create_client(url, key)
            logger.info("✓ Supabase客户端初始化成功")
        except Exception as e:
            logger.error(f"✗ Supabase初始化失败: {e}")
            raise

    # ==================== 用户管理 ====================

    def create_user(self, user_data: Dict) -> Dict:
        """
        创建新用户

        参数:
            user_data: 用户数据字典
                - username: 用户名
                - email: 邮箱（可选）
                - device_id: 设备ID（可选）

        返回:
            创建的用户数据
        """
        try:
            # 添加创建时间
            user_data['created_at'] = datetime.utcnow().isoformat()

            result = self.client.table('users').insert(user_data).execute()

            logger.info(f"用户创建成功: {user_data.get('username')}")
            return {
                'success': True,
                'data': result.data[0] if result.data else None
            }

        except Exception as e:
            logger.error(f"用户创建失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_user(self, user_id: int) -> Dict:
        """
        获取用户信息

        参数:
            user_id: 用户ID

        返回:
            用户数据
        """
        try:
            result = self.client.table('users').select('*').eq('id', user_id).execute()

            if result.data:
                return {
                    'success': True,
                    'data': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'error': '用户不存在'
                }

        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_or_create_user_by_device(self, device_id: str) -> Dict:
        """
        根据设备ID获取或创建用户

        参数:
            device_id: 设备ID

        返回:
            用户数据
        """
        try:
            # 先查询是否存在
            result = self.client.table('users').select('*').eq('device_id', device_id).execute()

            if result.data:
                logger.info(f"用户已存在: {device_id}")
                return {
                    'success': True,
                    'data': result.data[0],
                    'created': False
                }

            # 不存在则创建
            user_data = {
                'device_id': device_id,
                'username': f'用户_{device_id[:8]}'
            }

            return self.create_user(user_data)

        except Exception as e:
            logger.error(f"获取/创建用户失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_user(self, user_id: int, update_data: Dict) -> Dict:
        """
        更新用户信息

        参数:
            user_id: 用户ID
            update_data: 要更新的数据

        返回:
            更新结果
        """
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()

            result = self.client.table('users').update(update_data).eq('id', user_id).execute()

            logger.info(f"用户更新成功: {user_id}")
            return {
                'success': True,
                'data': result.data[0] if result.data else None
            }

        except Exception as e:
            logger.error(f"用户更新失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 对话记录管理 ====================

    def create_conversation(self, user_id: int, title: str = None) -> Dict:
        """
        创建新对话

        参数:
            user_id: 用户ID
            title: 对话标题（可选）

        返回:
            创建的对话数据
        """
        try:
            conversation_data = {
                'user_id': user_id,
                'title': title or '新对话',
                'created_at': datetime.utcnow().isoformat()
            }

            result = self.client.table('conversations').insert(conversation_data).execute()

            logger.info(f"对话创建成功: user_id={user_id}")
            return {
                'success': True,
                'data': result.data[0] if result.data else None
            }

        except Exception as e:
            logger.error(f"对话创建失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_conversations(self, user_id: int, limit: int = 50) -> Dict:
        """
        获取用户的对话列表

        参数:
            user_id: 用户ID
            limit: 返回数量限制

        返回:
            对话列表
        """
        try:
            result = self.client.table('conversations') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()

            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取对话列表失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_conversation(self, conversation_id: int) -> Dict:
        """
        获取对话详情

        参数:
            conversation_id: 对话ID

        返回:
            对话数据
        """
        try:
            result = self.client.table('conversations').select('*').eq('id', conversation_id).execute()

            if result.data:
                return {
                    'success': True,
                    'data': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'error': '对话不存在'
                }

        except Exception as e:
            logger.error(f"获取对话失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_conversation(self, conversation_id: int) -> Dict:
        """
        删除对话（及其消息）

        参数:
            conversation_id: 对话ID

        返回:
            删除结果
        """
        try:
            # 先删除对话关联的消息
            self.client.table('messages').delete().eq('conversation_id', conversation_id).execute()

            # 再删除对话
            result = self.client.table('conversations').delete().eq('id', conversation_id).execute()

            logger.info(f"对话删除成功: {conversation_id}")
            return {
                'success': True
            }

        except Exception as e:
            logger.error(f"对话删除失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 消息管理 ====================

    def add_message(self, conversation_id: int, role: str, content: str,
                   emotion_data: Dict = None, weather_data: Dict = None,
                   image_info: Dict = None) -> Dict:
        """
        添加消息

        参数:
            conversation_id: 对话ID
            role: 角色（user/assistant/system）
            content: 消息内容
            emotion_data: 心情分析数据（可选）
            weather_data: 天气数据（可选）
            image_info: 图片信息（可选）

        返回:
            创建的消息数据
        """
        try:
            message_data = {
                'conversation_id': conversation_id,
                'role': role,
                'content': content,
                'emotion_data': emotion_data,
                'weather_data': weather_data,
                'image_info': image_info,
                'created_at': datetime.utcnow().isoformat()
            }

            result = self.client.table('messages').insert(message_data).execute()

            logger.info(f"消息添加成功: conversation_id={conversation_id}, role={role}")
            return {
                'success': True,
                'data': result.data[0] if result.data else None
            }

        except Exception as e:
            logger.error(f"消息添加失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_messages(self, conversation_id: int, limit: int = 100) -> Dict:
        """
        获取对话的消息列表

        参数:
            conversation_id: 对话ID
            limit: 返回数量限制

        返回:
            消息列表
        """
        try:
            result = self.client.table('messages') \
                .select('*') \
                .eq('conversation_id', conversation_id) \
                .order('created_at', desc=False) \
                .limit(limit) \
                .execute()

            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取消息列表失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_nearby_conversations(self, latitude: float, longitude: float,
                                radius_km: float = 1.0, limit: int = 100) -> Dict:
        """
        查询指定位置附近的所有对话记录

        参数:
            latitude: 中心纬度
            longitude: 中心经度
            radius_km: 半径（公里），默认1公里
            limit: 返回数量限制

        返回:
            附近的消息列表
        """
        try:
            # 计算经纬度范围（粗略估算）
            # 1度约等于111公里
            lat_delta = radius_km / 111.0
            lon_delta = radius_km / (111.0 * abs(latitude) if latitude != 0 else 111.0)

            min_lat = latitude - lat_delta
            max_lat = latitude + lat_delta
            min_lon = longitude - lon_delta
            max_lon = longitude + lon_delta

            # 查询该范围内的所有对话消息
            # 首先获取该范围内的对话ID
            conv_result = self.client.table('conversations') \
                .select('id') \
                .gte('latitude', min_lat) \
                .lte('latitude', max_lat) \
                .gte('longitude', min_lon) \
                .lte('longitude', max_lon) \
                .limit(limit) \
                .execute()

            if not conv_result.data:
                return {
                    'success': True,
                    'data': [],
                    'count': 0
                }

            # 获取这些对话的消息
            conversation_ids = [c['id'] for c in conv_result.data]

            messages_result = self.client.table('messages') \
                .select('*') \
                .in_('conversation_id', conversation_ids) \
                .order('created_at', desc=False) \
                .limit(limit) \
                .execute()

            return {
                'success': True,
                'data': messages_result.data,
                'count': len(messages_result.data)
            }

        except Exception as e:
            logger.error(f"查询附近对话失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_recent_messages(self, conversation_id: int, count: int = 10) -> Dict:
        """
        获取最近的N条消息（用于上下文）

        参数:
            conversation_id: 对话ID
            count: 消息数量

        返回:
            消息列表
        """
        try:
            result = self.client.table('messages') \
                .select('*') \
                .eq('conversation_id', conversation_id) \
                .order('created_at', desc=True) \
                .limit(count) \
                .execute()

            # 反转顺序（最早的在前）
            messages = list(reversed(result.data))

            return {
                'success': True,
                'data': messages,
                'count': len(messages)
            }

        except Exception as e:
            logger.error(f"获取最近消息失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 位置记录管理 ====================

    def save_location(self, user_id: int, latitude: float, longitude: float,
                     weather_data: Dict = None) -> Dict:
        """
        保存用户位置信息

        参数:
            user_id: 用户ID
            latitude: 纬度
            longitude: 经度
            weather_data: 天气数据（可选）

        返回:
            创建的位置记录
        """
        try:
            location_data = {
                'user_id': user_id,
                'latitude': latitude,
                'longitude': longitude,
                'weather_data': weather_data,
                'created_at': datetime.utcnow().isoformat()
            }

            result = self.client.table('locations').insert(location_data).execute()

            logger.info(f"位置保存成功: user_id={user_id}")
            return {
                'success': True,
                'data': result.data[0] if result.data else None
            }

        except Exception as e:
            logger.error(f"位置保存失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_user_locations(self, user_id: int, limit: int = 50) -> Dict:
        """
        获取用户的位置历史

        参数:
            user_id: 用户ID
            limit: 返回数量限制

        返回:
            位置列表
        """
        try:
            result = self.client.table('locations') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()

            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取位置历史失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 图片记录管理 ====================

    def save_image(self, user_id: int, conversation_id: int,
                   image_base64: str, analysis_result: Dict = None) -> Dict:
        """
        保存上传的图片

        参数:
            user_id: 用户ID
            conversation_id: 对话ID
            image_base64: Base64编码的图片
            analysis_result: 图片分析结果（可选）

        返回:
            创建的图片记录
        """
        try:
            image_data = {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'image_data': image_base64,
                'analysis_result': analysis_result,
                'created_at': datetime.utcnow().isoformat()
            }

            result = self.client.table('images').insert(image_data).execute()

            logger.info(f"图片保存成功: user_id={user_id}")
            return {
                'success': True,
                'data': result.data[0] if result.data else None
            }

        except Exception as e:
            logger.error(f"图片保存失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_conversation_images(self, conversation_id: int) -> Dict:
        """
        获取对话中的所有图片

        参数:
            conversation_id: 对话ID

        返回:
            图片列表
        """
        try:
            result = self.client.table('images') \
                .select('*') \
                .eq('conversation_id', conversation_id) \
                .order('created_at', desc=False) \
                .execute()

            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取对话图片失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 统计分析 ====================

    def get_user_stats(self, user_id: int) -> Dict:
        """
        获取用户统计数据

        参数:
            user_id: 用户ID

        返回:
            统计数据
        """
        try:
            # 对话总数
            conv_result = self.client.table('conversations') \
                .select('id', count='exact') \
                .eq('user_id', user_id) \
                .execute()

            conversation_count = len(conv_result.data) if conv_result.data else 0

            # 消息总数
            msg_result = self.client.table('messages') \
                .select('id', count='exact') \
                .eq('conversation_id', 'in', \
                    [c['id'] for c in conv_result.data] if conv_result.data else []) \
                .execute()

            message_count = len(msg_result.data) if msg_result.data else 0

            # 图片总数
            img_result = self.client.table('images') \
                .select('id', count='exact') \
                .eq('user_id', user_id) \
                .execute()

            image_count = len(img_result.data) if img_result.data else 0

            return {
                'success': True,
                'data': {
                    'conversation_count': conversation_count,
                    'message_count': message_count,
                    'image_count': image_count
                }
            }

        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 健康检查 ====================

    def health_check(self) -> Dict:
        """
        检查数据库连接健康状态

        返回:
            健康状态
        """
        try:
            # 尝试简单查询
            result = self.client.table('users').select('id').limit(1).execute()

            return {
                'success': True,
                'status': 'healthy',
                'database': 'connected'
            }

        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return {
                'success': False,
                'status': 'unhealthy',
                'error': str(e)
            }
