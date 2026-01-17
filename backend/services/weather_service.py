"""
天气服务
使用Open-Meteo API查询天气（无需API key）
"""
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class WeatherService:
    """天气服务类"""

    def __init__(self, api_base: str = "https://api.open-meteo.com/v1"):
        self.api_base = api_base

    def get_weather_by_coords(self, latitude: float, longitude: float) -> Dict:
        """
        根据经纬度查询天气

        参数:
            latitude: 纬度
            longitude: 经度

        返回:
            包含天气信息的字典
        """
        try:
            # Open-Meteo API参数
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
                'hourly': 'temperature_2m,weather_code',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min',
                'timezone': 'auto'
            }

            # 发送请求
            response = requests.get(
                f"{self.api_base}/forecast",
                params=params,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            # 解析天气数据
            weather_info = self._parse_weather_data(data)

            logger.info(f"成功获取天气信息: {latitude}, {longitude}")
            return weather_info

        except requests.RequestException as e:
            logger.error(f"获取天气信息失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'weather_description': '无法获取天气信息'
            }

    def _parse_weather_data(self, data: Dict) -> Dict:
        """
        解析天气数据

        参数:
            data: API返回的原始数据

        返回:
            解析后的天气信息
        """
        try:
            current = data.get('current', {})
            daily = data.get('daily', {})

            # 获取当前天气代码
            weather_code = current.get('weather_code', 0)
            weather_description = self._get_weather_description(weather_code)

            # 构建返回数据
            result = {
                'success': True,
                'current': {
                    'temperature': current.get('temperature_2m'),
                    'humidity': current.get('relative_humidity_2m'),
                    'wind_speed': current.get('wind_speed_10m'),
                    'weather_code': weather_code,
                    'weather_description': weather_description
                },
                'daily': {
                    'max_temp': daily.get('temperature_2m_max', [])[0] if daily.get('temperature_2m_max') else None,
                    'min_temp': daily.get('temperature_2m_min', [])[0] if daily.get('temperature_2m_min') else None,
                },
                'location': {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude')
                },
                'weather_description': weather_description
            }

            return result

        except Exception as e:
            logger.error(f"解析天气数据失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'weather_description': '天气数据解析失败'
            }

    def _get_weather_description(self, code: int) -> str:
        """
        根据WMO天气代码获取中文描述

        参数:
            code: WMO天气代码

        返回:
            天气描述
        """
        weather_codes = {
            0: '晴朗',
            1: '大部分晴朗',
            2: '部分多云',
            3: '阴天',
            45: '雾',
            48: '沉积雾',
            51: '小毛毛雨',
            53: '中等毛毛雨',
            55: '密集毛毛雨',
            61: '小雨',
            63: '中雨',
            65: '大雨',
            71: '小雪',
            73: '中雪',
            75: '大雪',
            77: '雪粒',
            80: '阵雨',
            81: '强烈阵雨',
            82: '暴风雨',
            85: '小阵雪',
            86: '大阵雪',
            95: '雷雨',
            96: '雷暴伴冰雹',
            99: '强雷暴'
        }

        return weather_codes.get(code, '未知天气')

    def get_weather_summary(self, latitude: float, longitude: float) -> str:
        """
        获取天气摘要文本

        参数:
            latitude: 纬度
            longitude: 经度

        返回:
            天气摘要字符串
        """
        weather_info = self.get_weather_by_coords(latitude, longitude)

        if not weather_info.get('success'):
            return "无法获取当前天气信息"

        current = weather_info.get('current', {})

        temp = current.get('temperature')
        if temp is not None:
            desc = current.get('weather_description', '')
            humidity = current.get('humidity')
            wind = current.get('wind_speed')

            summary = f"当前天气{desc}，温度{temp}°C"

            if humidity:
                summary += f"，湿度{humidity}%"
            if wind:
                summary += f"，风速{wind}km/h"

            return summary
        else:
            return "天气信息暂时不可用"
