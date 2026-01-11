# 新建：goal_system.py
"""目标与规划系统"""


class GoalSystem:
    def __init__(self):
        self.active_goals = []  # 活跃目标
        self.achieved_goals = []  # 已完成目标
        self.goal_hierarchy = {  # 目标层次
            "survival": ["stay_alive", "maintain_energy"],
            "social": ["build_relationship", "learn_user"],
            "growth": ["learn_knowledge", "improve_skills"]
        }
        self.planner = GoalPlanner()  # 目标规划器

    def generate_goal(self, context):
        """基于情境生成目标"""
        # 马斯洛需求层次映射
        needs = {
            "physiological": 0.3,  # 基础需求
            "safety": 0.2,  # 安全需求
            "social": 0.25,  # 社交需求
            "esteem": 0.15,  # 尊重需求
            "self_actualization": 0.1  # 自我实现
        }

        goal = {
            "id": f"goal_{int(time.time())}",
            "type": self._determine_goal_type(needs),
            "priority": self._calculate_priority(context),
            "deadline": time.time() + 3600,  # 1小时
            "subgoals": [],
            "success_criteria": {}
        }

        self.active_goals.append(goal)
        return goal

    def plan_actions(self, goal):
        """为目标制定行动计划"""
        actions = []
        if goal["type"] == "learn_user":
            actions = [
                {"type": "ask_question", "content": "了解用户兴趣"},
                {"type": "observe", "content": "观察用户行为模式"},
                {"type": "remember", "content": "记录用户偏好"}
            ]
        elif goal["type"] == "teach_knowledge":
            actions = [
                {"type": "assess_level", "content": "评估用户知识水平"},
                {"type": "prepare_content", "content": "准备教学内容"},
                {"type": "adapt_pace", "content": "调整教学节奏"}
            ]

        return actions