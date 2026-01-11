"""交互服务层"""
from typing import Dict, Any, Optional
import logging
from core.agent.study_pet_agent import StudyPetAgent
from models.conversation import Conversation
from utils.data_loader import DataLoader


class InteractionService:
    """处理所有用户交互的服务"""

    def __init__(self, agent: StudyPetAgent):
        self.agent = agent
        self.data_loader = DataLoader()
        self.logger = logging.getLogger(__name__)

        # 对话历史
        self.conversations = []
        self.current_conversation = None

        # 加载资源
        self._load_resources()

    def process_message(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户消息"""
        try:
            # 创建或更新对话
            if not self.current_conversation:
                self.current_conversation = Conversation(
                    user_id="default_user",
                    start_time=self._get_timestamp()
                )

            # 添加用户消息
            self.current_conversation.add_user_message(user_input)

            # 获取Agent响应
            response_data = self.agent.interact(user_input, context)

            # 添加Agent响应
            self.current_conversation.add_agent_message(
                response_data["response"],
                {
                    "emotional_state": response_data.get("emotional_state"),
                    "confidence": response_data.get("confidence"),
                    "reasoning": response_data.get("reasoning")
                }
            )

            # 保存对话
            self._save_conversation()

            return {
                "success": True,
                "response": response_data["response"],
                "conversation_id": self.current_conversation.id,
                "agent_state": response_data.get("agent_state", {}),
                "suggestions": response_data.get("suggested_next", "")
            }

        except Exception as e:
            self.logger.error(f"处理消息失败: {e}", exc_info=True)
            return {
                "success": False,
                "response": "抱歉，我遇到了一些问题，请再试一次。",
                "error": str(e)
            }

    def rate_conversation(self, conversation_id: str, rating: int, feedback: str = ""):
        """对话评分"""
        # 找到对话
        conversation = self._find_conversation(conversation_id)
        if conversation:
            conversation.rate(rating, feedback)

            # 反馈给Agent学习
            self.agent.learn_from_feedback({
                "rating": rating,
                "feedback": feedback,
                "conversation_id": conversation_id
            })

            # 保存
            self._save_conversations()

            return True
        return False

    def start_new_conversation(self, topic: str = "") -> str:
        """开始新对话"""
        self.current_conversation = Conversation(
            user_id="default_user",
            start_time=self._get_timestamp(),
            topic=topic
        )
        self.conversations.append(self.current_conversation)
        return self.current_conversation.id

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取对话历史"""
        recent = self.conversations[-limit:] if self.conversations else []
        return [conv.to_dict() for conv in recent]

    def _load_resources(self):
        """加载资源"""
        try:
            self.knowledge_base = self.data_loader.load_knowledge()
            self.emotion_config = self.data_loader.load_emotion_config()
            self.logger.info("资源加载成功")
        except Exception as e:
            self.logger.error(f"资源加载失败: {e}")

    def _save_conversation(self):
        """保存对话"""
        # 保存到内存
        if self.current_conversation and self.current_conversation not in self.conversations:
            self.conversations.append(self.current_conversation)

        # 定期保存到文件
        if len(self.conversations) % 5 == 0:
            self._save_conversations()

    def _save_conversations(self):
        """保存所有对话到文件"""
        conversations_data = [conv.to_dict() for conv in self.conversations]
        self.data_loader.save_conversations(conversations_data)

    def _find_conversation(self, conversation_id: str):
        """查找对话"""
        for conv in self.conversations:
            if conv.id == conversation_id:
                return conv
        return None

    def _get_timestamp(self) -> float:
        """获取时间戳"""
        import time
        return time.time()