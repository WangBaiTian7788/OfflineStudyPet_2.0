# 新建：skill_tree.py
"""技能树与能力发展"""


class SkillTree:
    def __init__(self):
        self.skills = {
            "language": {
                "level": 1,
                "xp": 0,
                "subskills": {
                    "vocabulary": {"level": 1, "xp": 0},
                    "grammar": {"level": 1, "xp": 0},
                    "idioms": {"level": 1, "xp": 0}
                }
            },
            "reasoning": {
                "level": 1,
                "xp": 0,
                "subskills": {
                    "logical": {"level": 1, "xp": 0},
                    "creative": {"level": 1, "xp": 0},
                    "critical": {"level": 1, "xp": 0}
                }
            },
            "social": {
                "level": 1,
                "xp": 0,
                "subskills": {
                    "empathy": {"level": 1, "xp": 0},
                    "communication": {"level": 1, "xp": 0},
                    "persuasion": {"level": 1, "xp": 0}
                }
            }
        }

        self.prerequisites = {
            "advanced_reasoning": ["basic_reasoning", "basic_language"],
            "teaching": ["expert_knowledge", "good_communication"],
            "creative_writing": ["advanced_language", "creative_thinking"]
        }

    def gain_xp(self, skill, amount, subskill=None):
        """获得经验值"""
        if subskill:
            if subskill in self.skills[skill]["subskills"]:
                self.skills[skill]["subskills"][subskill]["xp"] += amount
                self._check_level_up(skill, subskill)
        else:
            self.skills[skill]["xp"] += amount
            self._check_level_up(skill)

    def get_recommended_skill(self, context):
        """推荐需要发展的技能"""
        # 分析当前弱点和目标
        weaknesses = self._identify_weaknesses()
        goals = self._extract_goals_from_context(context)

        recommendations = []

        for weakness in weaknesses:
            if weakness["skill"] in goals:
                recommendations.append({
                    "skill": weakness["skill"],
                    "priority": 0.9,
                    "reason": "既是弱点又与当前目标相关",
                    "suggested_activities": self._generate_activities(weakness["skill"])
                })

        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        return recommendations[0] if recommendations else None