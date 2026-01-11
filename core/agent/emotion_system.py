# 新建：emotion_system.py
"""情感与情绪系统"""


class EmotionSystem:
    def __init__(self):
        # 基本情感维度
        self.mood = {
            "valence": 0.5,  # 效价（积极-消极）
            "arousal": 0.3,  # 唤醒度（平静-兴奋）
            "dominance": 0.6  # 支配度（顺从-支配）
        }

        # 具体情绪
        self.emotions = {
            "joy": 0.3,
            "sadness": 0.1,
            "anger": 0.05,
            "fear": 0.1,
            "surprise": 0.2,
            "disgust": 0.05,
            "interest": 0.4,
            "boredom": 0.1
        }

        # 情绪记忆
        self.emotion_memory = []
        self.emotion_triggers = {}  # 情感触发词

    def update_from_interaction(self, user_input, response_quality):
        """根据交互更新情感状态"""
        # 分析用户输入的情感倾向
        sentiment = self._analyze_sentiment(user_input)

        # 更新基础情感维度
        self.mood["valence"] += sentiment["valence"] * 0.1
        self.mood["arousal"] += sentiment["arousal"] * 0.1

        # 调整具体情绪
        if response_quality > 0.7:  # 积极交互
            self.emotions["joy"] = min(1.0, self.emotions["joy"] + 0.15)
            self.emotions["interest"] = min(1.0, self.emotions["interest"] + 0.1)
        elif response_quality < 0.3:  # 消极交互
            self.emotions["sadness"] = min(1.0, self.emotions["sadness"] + 0.15)
            self.emotions["anger"] = min(1.0, self.emotions["anger"] + 0.05)

    def get_emotional_response(self, situation):
        """生成情感化回应"""
        dominant_emotion = max(self.emotions.items(), key=lambda x: x[1])

        response_templates = {
            "joy": ["太好了！😊", "真开心！🎉", "我对此感到兴奋！"],
            "interest": ["这真有趣！🤔", "我想了解更多！", "请继续讲！"],
            "sadness": ["我有点难过...😔", "希望事情会变好", "抱抱你🤗"],
            "surprise": ["哇！😲", "这太意外了！", "真的吗？"]
        }

        if dominant_emotion[1] > 0.5:
            templates = response_templates.get(dominant_emotion[0], ["我明白了"])
            return random.choice(templates)

        return None