# 新建：personality.py
"""个性特质系统（基于大五人格）"""


class Personality:
    def __init__(self):
        # 大五人格特质（OCEAN）
        self.traits = {
            "openness": 0.7,  # 开放性（高：好奇有创意；低：传统实用）
            "conscientiousness": 0.6,  # 尽责性（高：有条理可靠；低：随意灵活）
            "extraversion": 0.4,  # 外向性（高：外向活跃；低：内向安静）
            "agreeableness": 0.8,  # 宜人性（高：合作友善；低：竞争批判）
            "neuroticism": 0.3  # 神经质（高：敏感焦虑；低：稳定平静）
        }

        # 学习风格偏好
        self.learning_style = {
            "visual": 0.6,  # 视觉学习
            "auditory": 0.4,  # 听觉学习
            "kinesthetic": 0.3,  # 动觉学习
            "reading": 0.7  # 阅读学习
        }

    def influence_decision(self, options):
        """根据个性特质影响决策"""
        weighted_options = []

        for option in options:
            weight = 1.0

            # 开放性影响尝试新事物的意愿
            if "new" in option.get("tags", []):
                weight *= (0.5 + self.traits["openness"])

            # 外向性影响社交倾向
            if "social" in option.get("tags", []):
                weight *= (0.3 + self.traits["extraversion"])

            # 神经质影响风险承受
            if "risky" in option.get("tags", []):
                weight *= (1.2 - self.traits["neuroticism"])

            weighted_options.append((option, weight))

        # 根据权重选择
        return self._weighted_choice(weighted_options)