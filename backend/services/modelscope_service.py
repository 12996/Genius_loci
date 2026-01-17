"""
魔搭模型服务
调用魔搭API进行大模型推理
"""
import requests
import logging
import json
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelScopeService:
    """魔搭API服务类"""

    def __init__(self, api_key: str, api_base: str = "https://api-inference.modelscope.cn/v1"):
        self.api_key = api_key
        self.api_base = api_base
        self.default_model = "qwen/Qwen2.5-7B-Instruct"

        # 检查API key
        if not api_key:
            logger.warning("未设置魔搭API key，部分功能可能不可用")

    def _make_request(self, model: str, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> Dict:
        """
        发起API请求

        参数:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        返回:
            API响应
        """
        try:
            url = f"{self.api_base}/chat/completions"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise

    def generate_response(self, prompt: str, model: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """
        生成回复

        参数:
            prompt: 用户提示
            model: 模型名称（可选）
            system_prompt: 系统提示（可选）

        返回:
            模型回复文本
        """
        model = model or self.default_model

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self._make_request(model, messages)

            # 提取回复文本
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content']
            else:
                logger.error(f"API响应格式异常: {response}")
                return "抱歉，我暂时无法理解这个问题。"

        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            raise

    def analyze_image(self, image_base64: str, prompt: str = "请描述这张图片", model: Optional[str] = None) -> Dict:
        """
        分析图片（视觉模型）

        参数:
            image_base64: Base64编码的图片
            prompt: 分析提示
            model: 模型名称（可选）

        返回:
            分析结果
        """
        # 使用视觉模型
        model = model or "qwen/Qwen2-VL-7B-Instruct"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_base64}}
                ]
            }
        ]

        try:
            response = self._make_request(model, messages, max_tokens=500)

            if 'choices' in response and len(response['choices']) > 0:
                description = response['choices'][0]['message']['content']

                return {
                    'success': True,
                    'description': description,
                    'model': model
                }
            else:
                return {
                    'success': False,
                    'error': 'API响应格式异常'
                }

        except Exception as e:
            logger.error(f"图片分析失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def chat_with_context(self, message: str, context: str = "", image_info: Optional[str] = None,
                         weather_info: Optional[str] = None, emotion_info: Optional[str] = None) -> str:
        """
        带上下文的对话

        参数:
            message: 用户消息
            context: 对话上下文
            image_info: 图片信息（可选）
            weather_info: 天气信息（可选）
            emotion_info: 心情信息（可选）

        返回:
            回复文本
        """
        # 构建系统提示
        system_prompt = """你是"万物有灵"的灵体助手，你的特点：
1. 温暖、友善、富有同理心
2. 相信万物皆有灵
3. 善于从平凡事物中发现美好
4. 回复简洁（100字以内）
5. 语气轻松自然，像朋友聊天

当用户分享照片时，你会描述照片内容并讲述相关的故事。
当用户表达某种心情时，你会给予温暖的回应。"""

        # 构建用户消息
        user_message = message

        if image_info:
            user_message = f"[图片信息: {image_info}]\n\n用户说: {message}"

        if weather_info:
            user_message = f"[当前天气: {weather_info}]\n\n{user_message}"

        if emotion_info:
            user_message = f"[用户心情: {emotion_info}]\n\n{user_message}"

        if context:
            user_message = f"[对话上下文: {context}]\n\n{user_message}"

        try:
            response = self.generate_response(
                prompt=user_message,
                system_prompt=system_prompt
            )

            return response

        except Exception as e:
            logger.error(f"对话失败: {e}")
            return "我听到了你的声音，万物皆有灵性。"

    def identify_objects(self, image_base64: str) -> Dict:
        """
        识别图片中的物体

        参数:
            image_base64: Base64编码的图片

        返回:
            识别结果
        """
        prompt = """请分析这张图片，并以JSON格式返回：
{{
    "description": "详细描述图片内容（50字以内）",
    "objects": ["物体1", "物体2", "物体3"],
    "scene": "场景描述（20字以内）",
    "mood": "图片给人的感觉（10字以内）"
}}"""

        try:
            response = self.analyze_image(image_base64, prompt)

            if response.get('success'):
                # 尝试解析JSON
                description = response['description']

                try:
                    # 提取JSON部分
                    import re
                    json_match = re.search(r'\{.*\}', description, re.DOTALL)

                    if json_match:
                        result_data = json.loads(json_match.group())

                        return {
                            'success': True,
                            'description': result_data.get('description', description),
                            'objects': result_data.get('objects', []),
                            'scene': result_data.get('scene', ''),
                            'mood': result_data.get('mood', ''),
                            'raw_response': description
                        }

                except json.JSONDecodeError:
                    pass

                # 如果无法解析JSON，返回原始描述
                return {
                    'success': True,
                    'description': description,
                    'objects': [],
                    'raw_response': description
                }

            else:
                return response

        except Exception as e:
            logger.error(f"物体识别失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def is_available(self) -> bool:
        """
        检查服务是否可用

        返回:
            是否可用
        """
        return bool(self.api_key)
