"""主Agent类：协调所有子系统"""
import time
from typing import Dict, Any, Optional
from core.agent.central_executive import CentralExecutive
from core.memory.hierarchical_memory import HierarchicalMemory
from models.memory import Memory
from models.emotion import EmotionState


class StudyPetAgent:
    """智能学习桌宠Agent"""

    def __init__(self, name: str = "小桌"):
        self.name = name
        self.id = f"agent_{int(time.time())}"

        # 初始化子系统
        self.central_executive = CentralExecutive()
        self.memory = HierarchicalMemory()

        # 状态变量
        self.state = {
            "awake": True,
            "energy": 1.0,
            "curiosity": 0.7,
            "relationship_level": 0.3,
            "learning_motivation": 0.8,
            "social_desire": 0.6
        }

        # 当前目标
        self.current_goal = None
        self.goal_stack = []

        # 初始化时间
        self.creation_time = time.time()
        self.last_interaction = None

    def interact(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户交互"""
        # 更新内部状态
        self._update_state()

        # 处理输入
        if not self.state["awake"]:
            return self._get_sleep_response()

        # 创建交互上下文
        interaction_context = {
            "user_input": user_input,
            "context": context or {},
            "agent_state": self.state.copy(),
            "timestamp": time.time()
        }

        # 通过中央执行系统处理
        response_data = self.central_executive.process_interaction(interaction_context)

        # 更新记忆和状态
        self._update_from_interaction(user_input, response_data)

        return response_data

    def _update_state(self):
        """更新Agent状态"""
        # 能量衰减
        if self.state["awake"]:
            self.state["energy"] = max(0, self.state["energy"] - 0.01)
            if self.state["energy"] < 0.2:
                self.state["awake"] = False

    def _get_sleep_response(self) -> Dict[str, Any]:
        """获取睡眠状态响应"""
        return {
            "response": "Zzz... 我睡着了，需要休息一会儿...",
            "emotional_state": "sleepy",
            "suggested_action": "等待我醒来",
            "agent_state": self.state.copy()
        }

    def _update_from_interaction(self, user_input: str, response_data: Dict[str, Any]):
        """从交互中学习"""
        # 更新关系
        if "?" in user_input:
            self.state["curiosity"] = min(1.0, self.state["curiosity"] + 0.05)

        # 记录交互
        memory = Memory(
            content=user_input,
            response=response_data["response"],
            context={
                "emotional_state": response_data.get("emotional_state"),
                "agent_state": self.state.copy()
            }
        )
        self.memory.store(memory)

    def reflect(self) -> Dict[str, Any]:
        """自我反思"""
        return self.central_executive.self_reflect()

    def learn_from_feedback(self, feedback: Dict[str, Any]):
        """从反馈中学习"""
        self.central_executive.learn_from_feedback(feedback)

    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "creation_time": self.creation_time,
            "memory_stats": self.memory.get_stats(),
            "executive_state": self.central_executive.get_state()
        }