"""
Moments记录服务
用于管理moments表的CRUD操作
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from supabase import Client

logger = logging.getLogger(__name__)


class MomentsService:
    """Moments表服务类"""

    def __init__(self, client: Client):
        """
        初始化Moments服务

        参数:
            client: Supabase客户端实例
        """
        self.client = client

    # ==================== 创建 ====================

    def create_moment(self, user_id: str, latitude: float, longitude: float,
                      input_type: str, media_url: str = None,
                      sensor_context: Dict = None, user_mood_tag: str = None,
                      ai_narrative: str = None) -> Dict:
        """
        创建新的Moment记录

        参数:
            user_id: 用户ID (UUID)
            latitude: 纬度
            longitude: 经度
            input_type: 输入类型（如'image', 'text', 'voice'等）
            media_url: 媒体文件URL（可选）
            sensor_context: 传感器上下文数据（JSON）
            user_mood_tag: 用户心情标签
            ai_narrative: AI生成的叙述

        返回:
            创建的结果
        """
        try:
            moment_data = {
                'user_id': user_id,
                'latitude': latitude,
                'longitude': longitude,
                'input_type': input_type,
                'media_url': media_url,
                'sensor_context': sensor_context,
                'user_mood_tag': user_mood_tag,
                'ai_narrative': ai_narrative
            }

            # 移除None值
            moment_data = {k: v for k, v in moment_data.items() if v is not None}

            result = self.client.table('moments').insert(moment_data).execute()

            logger.info(f"Moment创建成功: user_id={user_id}")
            return {
                'success': True,
                'data': result.data[0] if result.data else None
            }

        except Exception as e:
            logger.error(f"Moment创建失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_moments_batch(self, moments_data: List[Dict]) -> Dict:
        """
        批量创建Moment记录

        参数:
            moments_data: Moment数据列表

        返回:
            创建的结果
        """
        try:
            # 清理None值
            cleaned_data = []
            for data in moments_data:
                cleaned_data.append({k: v for k, v in data.items() if v is not None})

            result = self.client.table('moments').insert(cleaned_data).execute()

            logger.info(f"批量创建Moment成功: {len(cleaned_data)}条")
            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"批量创建Moment失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 查询 ====================

    def get_moment_by_id(self, moment_id: str) -> Dict:
        """
        根据ID获取Moment记录

        参数:
            moment_id: Moment记录ID (UUID)

        返回:
            Moment数据
        """
        try:
            result = self.client.table('moments').select('*').eq('id', moment_id).execute()

            if result.data:
                return {
                    'success': True,
                    'data': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'error': 'Moment不存在'
                }

        except Exception as e:
            logger.error(f"获取Moment失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_moments_by_user(self, user_id: str, limit: int = 50,
                            offset: int = 0) -> Dict:
        """
        获取用户的所有Moment记录

        参数:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量（用于分页）

        返回:
            Moment列表
        """
        try:
            result = self.client.table('moments') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()

            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取用户Moments失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_moments_by_location(self, latitude: float, longitude: float,
                               radius_km: float = 1.0, limit: int = 50) -> Dict:
        """
        获取指定位置附近的Moment记录

        参数:
            latitude: 中心纬度
            longitude: 中心经度
            radius_km: 半径（公里）
            limit: 返回数量限制

        返回:
            Moment列表
        """
        try:
            # 简单的距离过滤（如果需要更精确的距离计算，可以使用PostGIS）
            # 1度约等于111km
            lat_delta = radius_km / 111.0
            lon_delta = radius_km / (111.0 * abs(latitude) / 90.0 if latitude != 0 else 111.0)

            result = self.client.table('moments') \
                .select('*') \
                .gte('latitude', latitude - lat_delta) \
                .lte('latitude', latitude + lat_delta) \
                .gte('longitude', longitude - lon_delta) \
                .lte('longitude', longitude + lon_delta) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()

            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取位置附近Moments失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_moments_by_mood(self, user_mood_tag: str, limit: int = 50) -> Dict:
        """
        根据心情标签获取Moment记录

        参数:
            user_mood_tag: 心情标签
            limit: 返回数量限制

        返回:
            Moment列表
        """
        try:
            result = self.client.table('moments') \
                .select('*') \
                .eq('user_mood_tag', user_mood_tag) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()

            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取心情Moments失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_recent_moments(self, limit: int = 20, offset: int = 0) -> Dict:
        """
        获取最近的Moment记录

        参数:
            limit: 返回数量限制
            offset: 偏移量

        返回:
            Moment列表
        """
        try:
            result = self.client.table('moments') \
                .select('*') \
                .order('created_at', desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()

            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取最近Moments失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def search_moments(self, filters: Dict = None, limit: int = 50) -> Dict:
        """
        根据多个条件搜索Moment记录

        参数:
            filters: 过滤条件字典
                - user_id: 用户ID
                - input_type: 输入类型
                - user_mood_tag: 心情标签
                - latitude: 纬度（用于位置查询）
                - longitude: 经度（用于位置查询）
                - radius_km: 查询半径（公里）
            limit: 返回数量限制

        返回:
            Moment列表
        """
        try:
            query = self.client.table('moments').select('*')

            # 应用过滤条件
            if filters:
                if 'user_id' in filters:
                    query = query.eq('user_id', filters['user_id'])

                if 'input_type' in filters:
                    query = query.eq('input_type', filters['input_type'])

                if 'user_mood_tag' in filters:
                    query = query.eq('user_mood_tag', filters['user_mood_tag'])

                # 位置查询
                if 'latitude' in filters and 'longitude' in filters:
                    lat = filters['latitude']
                    lon = filters['longitude']
                    radius = filters.get('radius_km', 1.0)

                    lat_delta = radius / 111.0
                    lon_delta = radius / (111.0 * abs(lat) / 90.0 if lat != 0 else 111.0)

                    query = query.gte('latitude', lat - lat_delta) \
                                 .lte('latitude', lat + lat_delta) \
                                 .gte('longitude', lon - lon_delta) \
                                 .lte('longitude', lon + lon_delta)

            result = query.order('created_at', desc=True).limit(limit).execute()

            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }

        except Exception as e:
            logger.error(f"搜索Moments失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 更新 ====================

    def update_moment(self, moment_id: str, update_data: Dict) -> Dict:
        """
        更新Moment记录

        参数:
            moment_id: Moment记录ID
            update_data: 要更新的数据

        返回:
            更新的结果
        """
        try:
            # 移除None值
            update_data = {k: v for k, v in update_data.items() if v is not None}

            result = self.client.table('moments') \
                .update(update_data) \
                .eq('id', moment_id) \
                .execute()

            if result.data:
                logger.info(f"Moment更新成功: {moment_id}")
                return {
                    'success': True,
                    'data': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'error': 'Moment不存在或更新失败'
                }

        except Exception as e:
            logger.error(f"Moment更新失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_ai_narrative(self, moment_id: str, ai_narrative: str) -> Dict:
        """
        更新Moment的AI叙述

        参数:
            moment_id: Moment记录ID
            ai_narrative: AI生成的叙述

        返回:
            更新的结果
        """
        return self.update_moment(moment_id, {'ai_narrative': ai_narrative})

    # ==================== 删除 ====================

    def delete_moment(self, moment_id: str) -> Dict:
        """
        删除Moment记录

        参数:
            moment_id: Moment记录ID

        返回:
            删除的结果
        """
        try:
            result = self.client.table('moments').delete().eq('id', moment_id).execute()

            logger.info(f"Moment删除成功: {moment_id}")
            return {
                'success': True
            }

        except Exception as e:
            logger.error(f"Moment删除失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_moments_batch(self, moment_ids: List[str]) -> Dict:
        """
        批量删除Moment记录

        参数:
            moment_ids: Moment ID列表

        返回:
            删除的结果
        """
        try:
            result = self.client.table('moments') \
                .delete() \
                .in_('id', moment_ids) \
                .execute()

            logger.info(f"批量删除Moment成功: {len(moment_ids)}条")
            return {
                'success': True,
                'count': len(moment_ids)
            }

        except Exception as e:
            logger.error(f"批量删除Moment失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 统计分析 ====================

    def get_user_moments_count(self, user_id: str) -> Dict:
        """
        获取用户的Moment记录总数

        参数:
            user_id: 用户ID

        返回:
            统计结果
        """
        try:
            result = self.client.table('moments') \
                .select('id', count='exact') \
                .eq('user_id', user_id) \
                .execute()

            count = len(result.data) if result.data else 0

            return {
                'success': True,
                'count': count
            }

        except Exception as e:
            logger.error(f"获取用户Moments统计失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_mood_distribution(self, user_id: str = None) -> Dict:
        """
        获取心情分布统计

        参数:
            user_id: 用户ID（可选，不指定则统计所有用户）

        返回:
            心情分布统计
        """
        try:
            query = self.client.table('moments').select('user_mood_tag')

            if user_id:
                query = query.eq('user_id', user_id)

            result = query.execute()

            # 统计各心情的数量
            mood_counts = {}
            for moment in result.data:
                mood = moment.get('user_mood_tag', 'unknown')
                mood_counts[mood] = mood_counts.get(mood, 0) + 1

            return {
                'success': True,
                'distribution': mood_counts,
                'total': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取心情分布失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_input_type_distribution(self, user_id: str = None) -> Dict:
        """
        获取输入类型分布统计

        参数:
            user_id: 用户ID（可选）

        返回:
            输入类型分布
        """
        try:
            query = self.client.table('moments').select('input_type')

            if user_id:
                query = query.eq('user_id', user_id)

            result = query.execute()

            # 统计各类型的数量
            type_counts = {}
            for moment in result.data:
                input_type = moment.get('input_type', 'unknown')
                type_counts[input_type] = type_counts.get(input_type, 0) + 1

            return {
                'success': True,
                'distribution': type_counts,
                'total': len(result.data)
            }

        except Exception as e:
            logger.error(f"获取输入类型分布失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== 实用方法 ====================

    def format_moment(self, moment_data: Dict) -> Dict:
        """
        格式化Moment数据用于显示

        参数:
            moment_data: 原始Moment数据

        返回:
            格式化后的数据
        """
        return {
            'id': moment_data.get('id'),
            'user_id': moment_data.get('user_id'),
            'location': {
                'latitude': moment_data.get('latitude'),
                'longitude': moment_data.get('longitude')
            },
            'input_type': moment_data.get('input_type'),
            'media_url': moment_data.get('media_url'),
            'sensor_context': moment_data.get('sensor_context', {}),
            'user_mood_tag': moment_data.get('user_mood_tag'),
            'ai_narrative': moment_data.get('ai_narrative'),
            'created_at': moment_data.get('created_at')
        }

    def enrich_moment_with_weather(self, moment_data: Dict, weather_service) -> Dict:
        """
        为Moment数据添加天气信息

        参数:
            moment_data: Moment数据
            weather_service: 天气服务实例

        返回:
            包含天气信息的Moment数据
        """
        try:
            lat = moment_data.get('latitude')
            lon = moment_data.get('longitude')

            if lat and lon:
                weather_info = weather_service.get_weather_by_coords(lat, lon)
                if weather_info.get('success'):
                    moment_data['weather'] = weather_info

            return moment_data

        except Exception as e:
            logger.error(f"添加天气信息失败: {e}")
            return moment_data
