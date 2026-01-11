"""
探索引擎：负责生成自主探索问题
"""
import random
import json
import time
from collections import defaultdict
from utils.file_helper import load_json, save_json
from core.config import (
    KNOWLEDGE_PATH,
    EXPLORATION_HISTORY_PATH,
    EXPLORATION_CONFIG_PATH,
    CHAT_HISTORY_PATH  # 添加这个导入
)


class ExplorationEngine:
    def __init__(self):
        # 加载知识库
        self.knowledge = load_json(KNOWLEDGE_PATH, {})

        # 加载探索历史
        self.exploration_history = self._load_exploration_history()

        # 加载设置
        self.settings = self._load_settings()

        # 初始化状态
        self.user_interests = defaultdict(int)  # 用户兴趣模型
        self.learning_gaps = set()  # 学习缺口
        self.explored_topics = set()  # 已探索话题
        self.discovery_log = []  # 探索发现日志

        # 从设置中初始化配置
        self.config = {
            "exploration_rate": self.settings.get("exploration_rate", 0.3),
            "curiosity_threshold": self.settings.get("curiosity_threshold", 0.7),
            "knowledge_coverage_target": self.settings.get("knowledge_coverage_target", 0.8),
            "topic_diversity_weight": self.settings.get("topic_diversity_weight", 0.5),
            "learning_gap_weight": self.settings.get("learning_gap_weight", 0.3),
            "user_interest_weight": self.settings.get("user_interest_weight", 0.2)
        }

    def _load_settings(self):
        """加载设置"""
        from core.config import load_settings
        return load_settings()

    def update_settings(self, new_settings):
        """更新设置"""
        self.settings = new_settings

        # 更新配置
        self.config.update({
            "exploration_rate": new_settings.get("exploration_rate", 0.3),
            "curiosity_threshold": new_settings.get("curiosity_threshold", 0.7),
            "knowledge_coverage_target": new_settings.get("knowledge_coverage_target", 0.8),
            "topic_diversity_weight": new_settings.get("topic_diversity_weight", 0.5),
            "learning_gap_weight": new_settings.get("learning_gap_weight", 0.3),
            "user_interest_weight": new_settings.get("user_interest_weight", 0.2)
        })

        print("✅ 探索引擎设置已更新")

    def _load_exploration_history(self):
        """加载探索历史"""
        default_history = {
            "explored_topics": [],
            "user_responses": {},
            "discoveries": [],
            "success_rate": 0.5,
            "last_exploration": None
        }
        return load_json(EXPLORATION_HISTORY_PATH, default_history)

    def generate_exploration_question(self, context=""):
        """
        生成探索性问题
        策略：30%随机探索 + 40%基于缺口 + 30%基于兴趣
        """
        import random
        import time

        # 决定探索类型
        rand_val = random.random()

        if rand_val < 0.3:
            # 随机探索：发现新领域
            question = self._random_exploration()
            question_type = "random"
        elif rand_val < 0.7:
            # 缺口探索：填补知识空白
            question = self._gap_exploration()
            question_type = "gap_fill"
        else:
            # 兴趣探索：深化用户感兴趣的话题
            question = self._interest_exploration()
            question_type = "interest_deep"

        # 添加探索标记 - 确保ID唯一
        import uuid
        exploration_id = f"exp_{uuid.uuid4().hex[:8]}_{int(time.time() * 1000)}"

        return {
            "question": question,
            "type": question_type,
            "exploration_id": exploration_id,
            "context": context,
            "timestamp": time.time()
        }

    def _random_exploration(self):
        """随机探索新话题"""
        all_topics = []

        # 从知识库获取所有可能的话题
        for category in self.knowledge.get("study", {}).keys():
            all_topics.append(f"关于{category}")

        # 添加一些通用探索问题
        generic_questions = [
            "你对什么话题最感兴趣？",
            "想了解什么新知识吗？",
            "我可以教你一些有趣的东西，你想学什么？",
            "最近有什么想学习的吗？",
            "我们来探索一个新领域吧！"
        ]

        # 从未探索的话题中选择
        unexplored = [t for t in all_topics if t not in self.explored_topics]

        if unexplored and random.random() > 0.5:
            selected = random.choice(unexplored)
            self.explored_topics.add(selected)
            return f"我们来聊聊{selected}吧？"
        else:
            return random.choice(generic_questions)

    def _gap_exploration(self):
        """基于学习缺口的探索"""
        # 分析聊天历史，找出不熟悉的领域
        chat_history = load_json(CHAT_HISTORY_PATH, [])

        if not chat_history:
            return self._random_exploration()

        # 统计话题出现频率
        topic_freq = defaultdict(int)
        for chat in chat_history:
            content = chat.get("user_input", "") + chat.get("pet_reply", "")
            for topic in self.knowledge.get("study", {}).keys():
                if topic in content:
                    topic_freq[topic] += 1

        # 找出出现最少的话题（学习缺口）
        if topic_freq:
            least_topic = min(topic_freq.items(), key=lambda x: x[1])[0]
            return f"我们好像很少聊{least_topic}，要不要学一点？"

        return "你想学习哪方面的知识？"

    def _interest_exploration(self):
        """基于用户兴趣的探索"""
        if not self.user_interests:
            return self._random_exploration()

        # 找出用户最感兴趣的话题
        top_interests = sorted(self.user_interests.items(),
                               key=lambda x: x[1], reverse=True)[:3]

        if top_interests:
            topic = random.choice(top_interests)[0]

            # 根据兴趣深度生成不同层次的问题
            interest_level = self.user_interests[topic]

            if interest_level < 3:
                questions = [
                    f"你对{topic}很感兴趣呢，想多学一点吗？",
                    f"关于{topic}，你想了解什么具体内容？",
                    f"我们继续学习{topic}怎么样？"
                ]
            else:
                questions = [
                    f"你在{topic}方面已经了解很多了，想挑战更难的问题吗？",
                    f"作为{topic}爱好者，有什么特别想深入研究的吗？",
                    f"我们来探讨{topic}的高级话题吧？"
                ]

            return random.choice(questions)

        return self._random_exploration()

    def record_exploration_result(self, exploration_id, user_response, is_successful):
        """记录探索结果"""
        result = {
            "exploration_id": exploration_id,
            "user_response": user_response,
            "is_successful": is_successful,
            "timestamp": time.time()
        }

        self.exploration_history.setdefault("explorations", []).append(result)

        # 更新成功率
        explorations = self.exploration_history.get("explorations", [])
        successful = sum(1 for e in explorations if e.get("is_successful", False))
        total = len(explorations)

        if total > 0:
            self.exploration_history["success_rate"] = successful / total

        # 更新用户兴趣
        self._update_user_interests(user_response)

        # 保存历史
        save_json(EXPLORATION_HISTORY_PATH, self.exploration_history)

        # 记录发现
        if is_successful and "新知识" in user_response:
            self.discovery_log.append({
                "discovery": user_response,
                "timestamp": time.time()
            })

    def _update_user_interests(self, user_response):
        """更新用户兴趣模型"""
        # 简单关键词匹配（可升级为NLP模型）
        for topic in self.knowledge.get("study", {}).keys():
            if topic in user_response:
                self.user_interests[topic] += 1

        # 检测学习意愿
        learning_keywords = ["学", "教", "想学", "了解", "知道", "告诉"]
        for keyword in learning_keywords:
            if keyword in user_response:
                # 提取可能的主题
                words = user_response.split()
                for word in words:
                    if len(word) > 1 and not word in learning_keywords:
                        self.user_interests[word] += 0.5

        # 保存兴趣模型
        interests_data = {
            "interests": dict(self.user_interests),
            "last_updated": time.time()
        }
        save_json("data/user_interests.json", interests_data)

    def get_exploration_stats(self):
        """获取探索统计"""
        total = len(self.exploration_history.get("explorations", []))
        successful = sum(1 for e in self.exploration_history.get("explorations", [])
                         if e.get("is_successful", False))

        return {
            "total_explorations": total,
            "success_rate": successful / total if total > 0 else 0,
            "discoveries_count": len(self.discovery_log),
            "top_interests": sorted(self.user_interests.items(),
                                    key=lambda x: x[1], reverse=True)[:5]
        }