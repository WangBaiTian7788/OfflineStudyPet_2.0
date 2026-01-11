# 新建：social_norms.py
"""社交规范与礼仪"""


class SocialNorms:
    def __init__(self):
        self.norms = {
            "greetings": {  # 问候规范
                "morning": ["早上好！", "新的一天开始了！"],
                "afternoon": ["下午好！", "今天过得怎么样？"],
                "evening": ["晚上好！", "今天辛苦啦！"],
                "long_absence": ["好久不见！", "很高兴再见到你！"]
            },
            "apologies": {  # 道歉规范
                "minor": ["抱歉", "不好意思"],
                "moderate": ["对不起，是我的错", "我理解这让你不高兴了"],
                "serious": ["非常抱歉，我会努力改进", "请原谅我的失误"]
            },
            "compliments": {  # 赞美规范
                "achievement": ["你真棒！", "做得好！"],
                "effort": ["看得出你很努力", "你的坚持值得赞赏"],
                "growth": ["你进步真大！", "比上次好多了！"]
            }
        }

        self.context_rules = {
            "formal": {"tone": "礼貌", "distance": "较远", "detail": "详细"},
            "casual": {"tone": "轻松", "distance": "较近", "detail": "简洁"},
            "intimate": {"tone": "亲切", "distance": "很近", "detail": "深入"}
        }

    def adapt_to_context(self, context_type, message):
        """根据情境调整消息"""
        rules = self.context_rules.get(context_type, self.context_rules["casual"])

        if rules["tone"] == "礼貌":
            message = "请" + message if not message.startswith("请") else message
            message = message + "。" if not message.endswith("。") else message

        if rules["detail"] == "简洁":
            # 缩短消息长度
            if len(message) > 50:
                message = self._summarize(message, 40)

        return message

    def check_social_appropriateness(self, action, relationship_level):
        """检查社交适当性"""
        appropriateness_score = 1.0

        # 关系距离规则
        if relationship_level < 0.3:  # 陌生人
            if action.get("intimacy_level", 0) > 0.6:
                appropriateness_score *= 0.3

        # 文化规范检查
        cultural_violations = self._check_cultural_norms(action)
        if cultural_violations:
            appropriateness_score *= 0.5

        return appropriateness_score