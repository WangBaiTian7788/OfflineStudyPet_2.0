import random
import os
from core.config import (
    KNOWLEDGE_PATH,
    CHAT_HISTORY_PATH,
    DIALOG_WEIGHTS_PATH,  # 添加这个导入
)
from utils.file_helper import load_json, save_json, generate_dialog_id
from core.knowledge.weight_manager import WeightManager


class LocalKnowledgeMatcher:
    def __init__(self):
        # 确保数据目录存在
        from utils.file_helper import init_data_dir
        init_data_dir()

        # 加载知识库
        self.knowledge = load_json(KNOWLEDGE_PATH)
        if not self.knowledge:
            raise FileNotFoundError(f"知识库文件 {KNOWLEDGE_PATH} 不存在，请检查路径")

        # 初始化权重管理器
        self.weight_manager = WeightManager()

        # 拆分用户学习内容（兼容文件不存在的情况，修复闪退核心）
        learned_json_path = os.path.join(os.path.dirname(KNOWLEDGE_PATH), "learned.json")
        self.learned_chat = load_json(learned_json_path, {"new_chat": [], "new_study": {}}).get("new_chat", [])
        self.learned_study = load_json(learned_json_path, {"new_chat": [], "new_study": {}}).get("new_study", {})

        from core.knowledge.exploration_engine import ExplorationEngine
        from core.memory.memory_network import MemoryNetwork
        from core.knowledge.learning_strategy import LearningStrategy

        self.exploration_engine = ExplorationEngine()
        self.memory_network = MemoryNetwork()
        self.learning_strategy = LearningStrategy()

    def initiate_exploration(self, context=""):
        """发起自主探索"""
        # 1. 决定是否探索（基于探索概率）
        import random

        # 移除调试信息
        rand_val = random.random()
        if rand_val > self.exploration_engine.config["exploration_rate"]:
            return None

        # 2. 获取学习策略建议
        strategy_action = self.learning_strategy.decide_next_action({"context": context})

        # 3. 生成探索问题
        exploration = self.exploration_engine.generate_exploration_question(context)

        # 4. 添加策略指导
        exploration["strategy_action"] = strategy_action

        return exploration

    def process_exploration_response(self, exploration_id, user_response):
        """处理探索响应"""
        # 判断是否成功
        is_successful = self._evaluate_exploration_success(user_response)

        # 记录探索结果
        self.exploration_engine.record_exploration_result(
            exploration_id, user_response, is_successful
        )

        # 更新学习策略
        self.learning_strategy.update_strategy({
            "successful": is_successful,
            "response": user_response
        })

        # 存储重要信息到记忆
        if is_successful and len(user_response) > 10:
            self.memory_network.store_memory(
                memory_type="discoveries",
                content={
                    "exploration_id": exploration_id,
                    "discovery": user_response,
                    "summary": f"用户回应：{user_response[:30]}..."
                },
                importance=0.7
            )

        return is_successful

    def _evaluate_exploration_success(self, response):
        """评估探索是否成功"""
        # 简单判断：如果回答长度足够且有内容，认为成功
        if len(response.strip()) < 3:
            return False

        negative_keywords = ["不知道", "不清楚", "没兴趣", "不想", "别问", "不太想", "不想聊", "不聊", "算了", "不要"]
        for keyword in negative_keywords:
            if keyword in response:
                return False

        positive_keywords = ["好", "可以", "想", "感兴趣", "学习", "了解"]
        for keyword in positive_keywords:
            if keyword in response:
                return True

        # 默认：中等长度回答视为成功
        return len(response.strip()) > 15

    def get_exploration_summary(self):
        """获取探索摘要"""
        stats = self.exploration_engine.get_exploration_stats()
        strategy = self.learning_strategy.get_strategy_summary()

        return {
            "exploration_stats": stats,
            "learning_strategy": strategy,
            "memory_stats": {
                "total_memories": sum(len(items) for items in self.memory_network.memories.values())
            }
        }

    # 需要添加到match_engine.py的LocalKnowledgeMatcher类中
    def get_active_content(self):
        """获取主动推送的内容（基于权重）"""
        try:
            # 1. 加载权重数据
            dialog_weights = load_json(DIALOG_WEIGHTS_PATH, {})

            # 2. 筛选高权重内容（权重 > 1.0）
            high_weight_items = [k for k, v in dialog_weights.items() if v > 1.0]

            if not high_weight_items:
                # 如果没有高权重内容，使用默认学习内容
                return self._get_default_study_content()

            # 3. 随机选择一个高权重对话ID
            selected_id = random.choice(high_weight_items)

            # 4. 从聊天记录中获取对应的内容
            chat_history = load_json(CHAT_HISTORY_PATH, [])
            for item in chat_history:
                if item.get("dialog_id") == selected_id:
                    return f"复习一下：{item.get('pet_reply', '学习内容')}"

            return self._get_default_study_content()
        except Exception as e:
            print(f"获取主动推送内容异常：{e}")
            return "今天也要好好学习哦！"

    def _get_default_study_content(self):
        """获取默认学习内容"""
        all_study = []
        # 原始学习内容
        for key, items in self.knowledge.get("study", {}).items():
            all_study.extend(items)
        # 用户新增的学习内容
        for key, items in self.learned_study.items():
            all_study.extend(items)

        if all_study:
            return random.choice(all_study)
        return "记得跟我聊天学习哦～"

    def match_chat(self, user_input):
        user_input = user_input.strip().lower()
        reply = ""
        dialog_id = generate_dialog_id()
        related_dialog_id = ""  # 用于关联学习内容的dialog_id

        # 1. 优先匹配用户教的闲聊（按权重筛选）
        matched_chat = []
        for item in self.learned_chat:
            if item.get("q", "").lower() in user_input:
                # 获取该学习内容的dialog_id（必须存在）
                chat_dialog_id = item.get("dialog_id", "")
                if not chat_dialog_id:
                    continue  # 没有dialog_id的内容跳过
                # 获取该内容的权重
                weight = self.weight_manager.get_dialog_weight(chat_dialog_id)
                matched_chat.append((item["a"], weight, chat_dialog_id))

        if matched_chat:
            # 过滤低权重内容（权重<0.5的直接排除）
            valid_chat = [x for x in matched_chat if x[1] > 0.5]
            if valid_chat:
                # 从高权重里随机选
                selected = random.choice(valid_chat)
                reply = selected[0]
                related_dialog_id = selected[2]  # 绑定学习内容的dialog_id
            else:
                # 所有匹配的都是低权重，返回默认回复
                reply = random.choice(self.knowledge.get("default_answer", ["我还在学习中～"]))
            # 保存聊天记录（关联学习内容的dialog_id）
            self._save_chat_record(dialog_id, user_input, reply, related_dialog_id)
            return reply, dialog_id

        # 2. 匹配原始知识库（逻辑不变）
        for item in self.knowledge.get("chat", []):
            for q in item.get("question", []):
                if q.lower() in user_input:
                    reply = random.choice(item.get("answer", []))
                    self._save_chat_record(dialog_id, user_input, reply)
                    return reply, dialog_id

        # 3. 无匹配返回默认回复
        reply = random.choice(self.knowledge.get("default_answer", ["我还在学习中～"]))
        self._save_chat_record(dialog_id, user_input, reply)
        return reply, dialog_id

    def match_study(self, study_type):
        """匹配学习内容"""
        try:
            reply = ""
            dialog_id = generate_dialog_id()

            # 1. 优先匹配用户教的学习内容
            if study_type in self.learned_study:
                user_study_items = self.learned_study[study_type]
                if user_study_items:
                    reply = random.choice(user_study_items)
                    self._save_chat_record(dialog_id, study_type, reply)
                    return reply, dialog_id

            # 2. 匹配原始知识库
            if study_type in self.knowledge.get("study", {}):
                knowledge_items = self.knowledge["study"][study_type]
                if knowledge_items:
                    reply = random.choice(knowledge_items)
                    self._save_chat_record(dialog_id, study_type, reply)
                    return reply, dialog_id

            # 3. 无匹配返回默认回复
            reply = "这个我还不太会，教教我吧～"
            self._save_chat_record(dialog_id, study_type, reply)
            return reply, dialog_id

        except Exception as e:
            print(f"匹配学习内容异常：{e}")
            reply = f"抱歉，我出错了：{str(e)}"
            dialog_id = generate_dialog_id()
            self._save_chat_record(dialog_id, study_type, reply)
            return reply, dialog_id

    def learn_from_user(self, user_input):
        user_input = user_input.strip()
        learned_json_path = os.path.join(os.path.dirname(KNOWLEDGE_PATH), "learned.json")
        # 加载learned.json（确保new_chat和new_study存在）
        learned_data = load_json(learned_json_path, {"new_chat": [], "new_study": {}})

        # 教闲聊：问 xxx -> 答 xxx
        if "->" in user_input:
            q_part, a_part = user_input.split("->")
            q = q_part.replace("问", "").strip()
            a = a_part.replace("答", "").strip()
            if q and a:
                # 强制生成唯一dialog_id，绑定到这个学习内容
                new_dialog_id = generate_dialog_id()
                learned_data["new_chat"].append({
                    "q": q,
                    "a": a,
                    "dialog_id": new_dialog_id  # 必须绑定dialog_id
                })
                save_json(learned_json_path, learned_data)
                self.learned_chat = learned_data["new_chat"]
                return f"我记住啦！下次问我【{q}】，我就会回答【{a}】"

        # 加知识点：逻辑不变
        elif user_input.startswith("加"):
            parts = user_input.replace("加", "").strip().split(" ", 1)
            if len(parts) == 2:
                stype, scontent = parts
                if stype not in learned_data["new_study"]:
                    learned_data["new_study"][stype] = []
                learned_data["new_study"][stype].append(scontent)
                save_json(learned_json_path, learned_data)
                self.learned_study = learned_data["new_study"]
                return f"新增【{stype}】知识点：{scontent}，我记住啦！"

        return "请用正确格式教我哦～\n1. 问 你叫什么 -> 答 我叫小桌\n2. 加 单词 pear - 梨"

    def get_study_trigger(self, user_input):
        """检测学习触发关键词"""
        try:
            all_types = list(self.knowledge.get("study", {}).keys()) + list(self.learned_study.keys())
            for t in all_types:
                if t in user_input:
                    return t
            return None
        except Exception as e:
            print(f"检测学习关键词异常：{e}")
            return None

    # match_engine.py 中的 _save_chat_record 方法，大约在第229行
    def _save_chat_record(self, dialog_id, user_input, pet_reply, related_dialog_id=""):
        import time
        from core.config import DEFAULT_WEIGHT  # 直接从config导入
        chat_history = load_json(CHAT_HISTORY_PATH, [])
        chat_history.append({
            "dialog_id": dialog_id,
            "user_input": user_input,
            "pet_reply": pet_reply,
            "related_dialog_id": related_dialog_id,
            "timestamp": int(time.time() * 1000),
            "rating": None,
            "weight": DEFAULT_WEIGHT  # 使用从config导入的常量
        })
        save_json(CHAT_HISTORY_PATH, chat_history)
