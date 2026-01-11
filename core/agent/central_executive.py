"""中央执行系统"""
from typing import Dict, Any, List
import time
from core.agent.emotion_system import EmotionSystem
from core.agent.personality import Personality
from core.agent.goal_system import GoalSystem
from core.agent.metacognition import Metacognition
from core.agent.theory_of_mind import TheoryOfMind


class CentralExecutive:
    """中央执行系统 - 协调各子系统"""

    def __init__(self):
        # 初始化子系统
        self.emotion_system = EmotionSystem()
        self.personality = Personality()
        self.goal_system = GoalSystem()
        self.metacognition = Metacognition()
        self.theory_of_mind = TheoryOfMind()

        # 工作记忆
        self.working_memory = {
            "current_focus": None,
            "recent_inputs": [],
            "active_goals": [],
            "emotional_context": {}
        }

        # 注意力资源
        self.attention_resources = 1.0

        # 决策历史
        self.decision_history = []

    def process_interaction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理交互的全流程"""
        # 1. 注意力分配
        self._allocate_attention(context)

        # 2. 情感处理
        emotional_state = self.emotion_system.process(context)

        # 3. 心智理论推断
        user_state = self.theory_of_mind.infer_user_state(context)

        # 4. 目标评估
        relevant_goals = self.goal_system.evaluate(context, user_state)

        # 5. 生成响应选项
        response_options = self._generate_response_options(
            context, emotional_state, user_state, relevant_goals
        )

        # 6. 个性过滤
        filtered_responses = self.personality.filter_responses(response_options)

        # 7. 元认知监控
        final_response = self.metacognition.select_response(
            filtered_responses, context
        )

        # 8. 记录决策
        self._record_decision({
            "context": context,
            "options": response_options,
            "selected": final_response,
            "timestamp": time.time()
        })

        return {
            "response": final_response["text"],
            "emotional_state": emotional_state.get_dominant(),
            "confidence": final_response["confidence"],
            "reasoning": final_response.get("reasoning", ""),
            "suggested_next": self._suggest_next_action(context)
        }

    def self_reflect(self) -> Dict[str, Any]:
        """自我反思"""
        reflections = []

        # 情感反思
        reflections.append(self.emotion_system.reflect())

        # 目标反思
        reflections.append(self.goal_system.reflect())

        # 元认知反思
        reflections.append(self.metacognition.reflect())

        # 综合反思
        return {
            "timestamp": time.time(),
            "reflections": reflections,
            "insights": self._extract_insights(reflections),
            "improvement_plan": self._generate_improvement_plan(reflections)
        }

    def learn_from_feedback(self, feedback: Dict[str, Any]):
        """从反馈中学习"""
        # 情感学习
        self.emotion_system.learn_from_feedback(feedback)

        # 目标调整
        self.goal_system.adjust_from_feedback(feedback)

        # 元认知更新
        self.metacognition.update_from_feedback(feedback)

    def _allocate_attention(self, context: Dict[str, Any]):
        """分配注意力资源"""
        # 简化实现
        self.working_memory["current_focus"] = context.get("user_input", "")

    def _generate_response_options(self, context, emotional_state, user_state, goals):
        """生成响应选项"""
        # 根据情境生成多种可能的响应
        options = []

        # 情感响应
        emotional_responses = emotional_state.generate_responses()
        options.extend(emotional_responses)

        # 目标导向响应
        goal_responses = self.goal_system.generate_responses(goals, context)
        options.extend(goal_responses)

        # 社交响应
        social_responses = self.theory_of_mind.generate_responses(user_state)
        options.extend(social_responses)

        return options

    def _suggest_next_action(self, context: Dict[str, Any]) -> str:
        """建议下一步行动"""
        suggestions = [
            "你想继续聊这个话题吗？",
            "我们学习新知识怎么样？",
            "需要我帮你复习吗？",
            "想听听我的想法吗？"
        ]

        # 根据情境选择建议
        if "学习" in context.get("user_input", ""):
            return "我们可以深入探讨这个话题"
        elif "？" in context.get("user_input", ""):
            return "还有其他问题吗？"

        return suggestions[0]

    def _record_decision(self, decision: Dict[str, Any]):
        """记录决策"""
        self.decision_history.append(decision)
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-100:]

    def _extract_insights(self, reflections: List[Dict[str, Any]]) -> List[str]:
        """从反思中提取洞察"""
        insights = []
        for reflection in reflections:
            if "insight" in reflection:
                insights.append(reflection["insight"])
        return insights[:3]

    def _generate_improvement_plan(self, reflections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成改进计划"""
        return {
            "emotional_improvements": self.emotion_system.get_improvement_suggestions(),
            "goal_adjustments": self.goal_system.get_adjustment_suggestions(),
            "learning_focus": self.metacognition.get_learning_focus()
        }

    def get_state(self) -> Dict[str, Any]:
        """获取执行系统状态"""
        return {
            "attention_resources": self.attention_resources,
            "working_memory_focus": self.working_memory["current_focus"],
            "emotion_state": self.emotion_system.get_state(),
            "active_goals_count": len(self.working_memory["active_goals"]),
            "decision_history_count": len(self.decision_history)
        }