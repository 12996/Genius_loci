"""
心情分析服务
使用大模型分析用户的心情
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class EmotionService:
    """心情分析服务类"""

    # 心情关键词映射
    EMOTION_KEYWORDS = {
        'happy': ['开心', '快乐', '高兴', '幸福', '愉快', '兴奋', '喜悦', '满足', '舒服'],
        'sad': ['难过', '伤心', '悲伤', '痛苦', '失落', '沮丧', '郁闷', '伤心', '哭泣'],
        'angry': ['生气', '愤怒', '恼火', '烦躁', '气愤', '不爽', '讨厌'],
        'anxious': ['焦虑', '紧张', '担心', '害怕', '恐惧', '不安', '忧虑'],
        'surprised': ['惊讶', '震惊', '意外', '吃惊', '不可思议'],
        'calm': ['平静', '宁静', '安详', '淡定', '平和'],
        'tired': ['累', '疲惫', '疲倦', '困', '乏力', '没精神'],
        'excited': ['激动', '兴奋', '热情', '期待'],
        'confused': ['困惑', '迷茫', '不解', '疑惑'],
        'grateful': ['感谢', '感激', '谢谢', '感恩']
    }

    # 心情对应的描述和建议
    EMOTION_RESPONSES = {
        'happy': {
            'description': '心情愉悦',
            'emoji': '😊',
            'suggestions': ['继续保持好心情！', '美好的日子值得分享！', '开心是最棒的治愈！']
        },
        'sad': {
            'description': '心情低落',
            'emoji': '😢',
            'suggestions': ['抱抱你，一切都会好起来的', '允许自己难过一会儿吧', '试着和朋友聊聊？']
        },
        'angry': {
            'description': '心情愤怒',
            'emoji': '😠',
            'suggestions': ['深呼吸，放松一下', '出去走走散散心', '听些舒缓的音乐']
        },
        'anxious': {
            'description': '心情焦虑',
            'emoji': '😰',
            'suggestions': ['一步步来，不要急', '相信自己能行', '休息一下再继续']
        },
        'surprised': {
            'description': '心情惊讶',
            'emoji': '😲',
            'suggestions': ['意外总是不期而遇', '这真是意想不到！', '生活充满惊喜']
        },
        'calm': {
            'description': '心情平静',
            'emoji': '😌',
            'suggestions': ['保持内心的宁静', '平静也是一种力量', '享受当下的美好']
        },
        'tired': {
            'description': '心情疲惫',
            'emoji': '😴',
            'suggestions': ['好好休息一下吧', '身体需要充电了', '休息是为了走更远的路']
        },
        'excited': {
            'description': '心情激动',
            'emoji': '🤩',
            'suggestions': ['这份热情很珍贵！', '将激动化为行动力！', '享受这份激动吧']
        },
        'confused': {
            'description': '心情困惑',
            'emoji': '😕',
            'suggestions': ['给自己一点时间思考', '也许答案很快就会浮现', '慢慢来，不着急']
        },
        'grateful': {
            'description': '心情感恩',
            'emoji': '🙏',
            'suggestions': ['感恩让生活更美好', '谢谢你的善意', '传递这份感恩吧']
        },
        'neutral': {
            'description': '心情平和',
            'emoji': '😐',
            'suggestions': ['平平淡淡才是真', '每一天都值得珍惜', '保持平衡很好']
        }
    }

    def analyze_emotion(self, text: str) -> Dict:
        """
        分析文本中的心情

        参数:
            text: 用户输入的文本

        返回:
            包含心情分析结果的字典
        """
        if not text or not text.strip():
            return {
                'success': False,
                'error': '文本为空'
            }

        try:
            # 统计每种心情的匹配次数
            emotion_scores = {}

            for emotion, keywords in self.EMOTION_KEYWORDS.items():
                score = 0
                matched_keywords = []

                for keyword in keywords:
                    if keyword in text:
                        score += text.count(keyword)
                        matched_keywords.append(keyword)

                if score > 0:
                    emotion_scores[emotion] = {
                        'score': score,
                        'keywords': matched_keywords
                    }

            # 判断主要心情
            if emotion_scores:
                # 找出得分最高的心情
                primary_emotion = max(emotion_scores.items(), key=lambda x: x[1]['score'])[0]

                # 获取该心情的详细信息
                emotion_info = self.EMOTION_RESPONSES.get(primary_emotion, self.EMOTION_RESPONSES['neutral'])

                result = {
                    'success': True,
                    'primary_emotion': primary_emotion,
                    'description': emotion_info['description'],
                    'emoji': emotion_info['emoji'],
                    'matched_keywords': emotion_scores[primary_emotion]['keywords'],
                    'suggestions': emotion_info['suggestions'],
                    'all_emotions': list(emotion_scores.keys())
                }

                logger.info(f"分析心情成功: {primary_emotion}, 关键词: {emotion_scores[primary_emotion]['keywords']}")
                return result

            else:
                # 未检测到明确心情，返回中性
                result = {
                    'success': True,
                    'primary_emotion': 'neutral',
                    'description': '心情平和',
                    'emoji': '😐',
                    'matched_keywords': [],
                    'suggestions': self.EMOTION_RESPONSES['neutral']['suggestions'],
                    'all_emotions': ['neutral']
                }

                logger.info("未检测到明确心情，返回中性")
                return result

        except Exception as e:
            logger.error(f"分析心情失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_emotion_summary(self, text: str) -> str:
        """
        获取心情分析摘要文本

        参数:
            text: 用户输入的文本

        返回:
            心情摘要字符串
        """
        analysis = self.analyze_emotion(text)

        if not analysis.get('success'):
            return "暂时无法分析心情"

        emoji = analysis.get('emoji', '')
        description = analysis.get('description', '')
        keywords = analysis.get('matched_keywords', [])

        summary = f"{emoji} {description}"

        if keywords:
            summary += f"（检测到关键词：{', '.join(keywords)}）"

        return summary

    def get_emotion_suggestion(self, text: str) -> str:
        """
        根据心情获取建议

        参数:
            text: 用户输入的文本

        返回:
            建议字符串
        """
        analysis = self.analyze_emotion(text)

        if not analysis.get('success'):
            return "照顾好自己的心情很重要"

        suggestions = analysis.get('suggestions', [])
        if suggestions:
            import random
            return random.choice(suggestions)

        return "保持好心情"

    def analyze_with_llm(self, text: str, llm_service) -> Dict:
        """
        使用大模型进行更深入的心情分析

        参数:
            text: 用户输入的文本
            llm_service: 大模型服务实例

        返回:
            包含心情分析结果的字典
        """
        # 先使用关键词分析
        basic_analysis = self.analyze_emotion(text)

        # 使用大模型进行更深入的分析
        prompt = f"""你是一个心情分析助手
请分析以下文本中的用户心情，并给出简短的回复。

用户文本: {text}

返回用户的心情


注意：
1. 你的返回有且只有这四种-  
- 难过
- 开心
- 平静
- 神秘
- 愤怒
- 迷茫

"""

        try:
            response = llm_service.generate_response(prompt)
            if '难过' in response:
                response = '难过'
            if '开心' in response:
                response = '开心'
            if '平静' in response:
                response = '平静'
            if '神秘' in response:
                response = '神秘'
            if '愤怒' in response:
                response = '愤怒'
            if '迷茫' in response:
                response = '迷茫'
            print(response)
            return response

        except Exception as e:
            logger.error(f"大模型心情分析失败: {e}")
            return basic_analysis
