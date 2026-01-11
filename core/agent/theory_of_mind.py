# 新建：theory_of_mind.py
"""心智理论 - 理解他人心理状态"""


class TheoryOfMind:
    def __init__(self):
        self.user_model = {  # 用户心理模型
            "beliefs": {},  # 用户相信什么
            "desires": {},  # 用户想要什么
            "intentions": {},  # 用户打算做什么
            "knowledge": {},  # 用户知道什么
            "emotional_state": {}  # 用户情绪状态
        }

        self.attribution_style = "balanced"  # 归因风格

    def infer_mental_state(self, user_actions, context):
        """从行为推断心理状态"""
        inferences = {}

        # 推断信念
        if "ask_question" in user_actions:
            topic = self._extract_topic(user_actions["ask_question"])
            inferences["beliefs"] = {
                "topic": topic,
                "confidence": 0.7,
                "inference": f"用户相信我不了解{topic}，或者想测试我的知识"
            }

        # 推断意图
        if "teaching" in user_actions:
            content = user_actions["teaching"]
            inferences["intentions"] = {
                "primary": "educate",
                "secondary": "test_comprehension",
                "confidence": 0.8
            }

        # 更新用户模型
        self._update_user_model(inferences)
        return inferences

    def predict_user_reaction(self, proposed_action):
        """预测用户对某行动的反应"""
        predictions = []

        # 基于用户模型预测
        if "prefers_directness" in self.user_model.get("desires", {}):
            if proposed_action.get("style") == "direct":
                predictions.append({
                    "reaction": "positive",
                    "confidence": 0.8,
                    "reason": "用户喜欢直接交流"
                })

        # 基于历史相似情况预测
        historical_similar = self._find_similar_historical(proposed_action)
        if historical_similar:
            for case in historical_similar:
                predictions.append({
                    "reaction": case["actual_reaction"],
                    "confidence": case["similarity"] * 0.9,
                    "reason": f"与历史情况相似（{case['similarity']:.1%}）"
                })

        return predictions