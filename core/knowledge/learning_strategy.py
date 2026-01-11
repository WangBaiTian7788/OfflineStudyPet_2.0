"""
学习策略：决定探索方向和深度
"""
import random
from enum import Enum
from datetime import datetime, timedelta


class LearningPhase(Enum):
    DISCOVERY = 1  # 发现阶段：广泛探索
    DEEPENING = 2  # 深化阶段：深入特定领域
    INTEGRATION = 3  # 整合阶段：连接不同知识
    MASTERY = 4  # 精通阶段：应用和创造


class LearningStrategy:
    def __init__(self):
        self.current_phase = LearningPhase.DISCOVERY
        self.phase_start_time = datetime.now()

        # 学习进度跟踪
        self.progress = {
            "topics_explored": set(),
            "concepts_mastered": set(),
            "questions_asked": 0,
            "successful_explorations": 0
        }

        # 自适应参数
        self.parameters = {
            "exploration_vs_exploitation": 0.7,  # 探索 vs 利用的平衡
            "difficulty_level": 0.3,  # 当前难度水平
            "curiosity_level": 0.8,  # 好奇心水平
            "persistence": 0.5  # 坚持程度
        }

    def decide_next_action(self, context):
        """决定下一步行动"""
        current_time = datetime.now()
        phase_duration = (current_time - self.phase_start_time).days

        # 根据学习阶段调整策略
        if self.current_phase == LearningPhase.DISCOVERY:
            return self._discovery_strategy(context)
        elif self.current_phase == LearningPhase.DEEPENING:
            return self._deepening_strategy(context)
        elif self.current_phase == LearningPhase.INTEGRATION:
            return self._integration_strategy(context)
        else:  # MASTERY
            return self._mastery_strategy(context)

    def _discovery_strategy(self, context):
        """发现阶段策略：广泛探索"""
        actions = [
            {
                "type": "explore_new_topic",
                "probability": 0.4,
                "description": "探索全新话题"
            },
            {
                "type": "ask_open_question",
                "probability": 0.3,
                "description": "提问开放式问题"
            },
            {
                "type": "test_assumption",
                "probability": 0.2,
                "description": "测试假设"
            },
            {
                "type": "seek_feedback",
                "probability": 0.1,
                "description": "寻求反馈"
            }
        ]

        return self._select_action_by_probability(actions)

    def _deepening_strategy(self, context):
        """深化阶段策略：深入已有话题"""
        # 如果某个话题已经有基础，就深化
        if context.get("current_topic"):
            return {
                "type": "deepen_topic",
                "topic": context["current_topic"],
                "action": "ask_detailed_question"
            }

        actions = [
            {
                "type": "ask_comparison",
                "probability": 0.3,
                "description": "询问比较性问题"
            },
            {
                "type": "explore_application",
                "probability": 0.3,
                "description": "探索实际应用"
            },
            {
                "type": "seek_principles",
                "probability": 0.2,
                "description": "寻找基本原理"
            },
            {
                "type": "challenge_understanding",
                "probability": 0.2,
                "description": "挑战现有理解"
            }
        ]

        return self._select_action_by_probability(actions)

    def _integration_strategy(self, context):
        """整合阶段策略：连接不同知识"""
        actions = [
            {
                "type": "find_connections",
                "probability": 0.4,
                "description": "寻找知识间的联系"
            },
            {
                "type": "build_framework",
                "probability": 0.3,
                "description": "构建知识框架"
            },
            {
                "type": "identify_patterns",
                "probability": 0.2,
                "description": "识别模式"
            },
            {
                "type": "create_analogy",
                "probability": 0.1,
                "description": "创建类比"
            }
        ]

        return self._select_action_by_probability(actions)

    def _mastery_strategy(self, context):
        """精通阶段策略：应用和创造"""
        actions = [
            {
                "type": "apply_knowledge",
                "probability": 0.4,
                "description": "应用知识解决问题"
            },
            {
                "type": "teach_concept",
                "probability": 0.3,
                "description": "尝试教授概念"
            },
            {
                "type": "create_new",
                "probability": 0.2,
                "description": "创造新内容"
            },
            {
                "type": "critique_ideas",
                "probability": 0.1,
                "description": "批判性评价"
            }
        ]

        return self._select_action_by_probability(actions)

    def _select_action_by_probability(self, actions):
        """根据概率选择行动"""
        rand_val = random.random()
        cumulative = 0

        for action in actions:
            cumulative += action["probability"]
            if rand_val <= cumulative:
                return action

        return actions[-1]  # 兜底

    def update_strategy(self, exploration_result):
        """根据探索结果更新策略"""
        # 更新进度
        self.progress["questions_asked"] += 1

        if exploration_result.get("successful"):
            self.progress["successful_explorations"] += 1

            # 如果探索成功，稍微增加难度
            self.parameters["difficulty_level"] = min(
                1.0, self.parameters["difficulty_level"] + 0.05
            )
        else:
            # 如果失败，稍微降低难度
            self.parameters["difficulty_level"] = max(
                0.1, self.parameters["difficulty_level"] - 0.05
            )

        # 更新好奇心（随着成功探索而增加）
        recent_success_rate = (
                self.progress["successful_explorations"] /
                max(1, self.progress["questions_asked"])
        )
        self.parameters["curiosity_level"] = 0.5 + recent_success_rate * 0.5

        # 检查是否需要切换学习阶段
        self._check_phase_transition()

    def _check_phase_transition(self):
        """检查是否需要切换学习阶段"""
        phase_duration = (datetime.now() - self.phase_start_time).days

        # 简单的阶段切换规则
        if (self.current_phase == LearningPhase.DISCOVERY and
                phase_duration > 3 and
                len(self.progress["topics_explored"]) >= 5):
            self.current_phase = LearningPhase.DEEPENING
            self.phase_start_time = datetime.now()

        elif (self.current_phase == LearningPhase.DEEPENING and
              phase_duration > 5 and
              len(self.progress["concepts_mastered"]) >= 3):
            self.current_phase = LearningPhase.INTEGRATION
            self.phase_start_time = datetime.now()

        elif (self.current_phase == LearningPhase.INTEGRATION and
              phase_duration > 7):
            self.current_phase = LearningPhase.MASTERY
            self.phase_start_time = datetime.now()

    def get_strategy_summary(self):
        """获取策略摘要"""
        return {
            "current_phase": self.current_phase.name,
            "phase_duration_days": (datetime.now() - self.phase_start_time).days,
            "progress": self.progress,
            "parameters": self.parameters
        }


# 扩展learning_strategy.py
class AdaptiveLearningStrategy(LearningStrategy):
    """自适应学习策略"""

    def __init__(self):
        super().__init__()
        self.learning_styles = {
            "deep": 0.6,  # 深度学习
            "broad": 0.4,  # 广度学习
            "spaced": 0.7,  # 间隔学习
            "interleaved": 0.3  # 交错学习
        }

        self.mastery_levels = {}  # 各领域掌握程度
        self.learning_goals = []  # 学习目标

    def select_learning_method(self, topic, context):
        """根据情境选择学习方法"""
        methods = []

        # 基于掌握程度
        mastery = self.mastery_levels.get(topic, 0.3)
        if mastery < 0.3:
            methods.append({"name": "foundation", "weight": 0.8})
        elif mastery < 0.7:
            methods.append({"name": "practice", "weight": 0.7})
        else:
            methods.append({"name": "mastery", "weight": 0.6})

        # 基于学习风格
        if self.learning_styles["deep"] > 0.6:
            methods.append({"name": "deep_dive", "weight": 0.9})
        if self.learning_styles["broad"] > 0.6:
            methods.append({"name": "overview", "weight": 0.8})

        # 基于上下文
        if context.get("time_available", 0) < 300:  # 少于5分钟
            methods.append({"name": "micro_learning", "weight": 1.0})

        return self._select_weighted_method(methods)