"""
记忆网络：存储和检索探索结果（修复版）
"""
import json
import uuid
import time
from datetime import datetime
from collections import defaultdict
from utils.file_helper import load_json, save_json


class MemoryNetwork:
    def __init__(self):
        # 确保数据目录存在
        from utils.file_helper import init_data_dir
        init_data_dir()

        self.memory_file = "data/exploration_memory.json"
        self.memories = self._load_memories()

        # 记忆关联网络 - 确保先初始化
        self.association_graph = defaultdict(set)
        try:
            self._build_association_graph()
        except Exception as e:
            print(f"构建关联图时出错: {e}")
            # 确保 association_graph 至少是一个空的 defaultdict(set)
            self.association_graph = defaultdict(set)

    def _load_memories(self):
        """加载记忆"""
        default_memories = {
            "facts": [],
            "preferences": [],
            "conversations": [],
            "discoveries": [],
            "timeline": []
        }
        return load_json(self.memory_file, default_memories)

    def _build_association_graph(self):
        """构建记忆关联图"""
        try:
            # 确保 self.memories 是字典
            if not isinstance(self.memories, dict):
                self.memories = {
                    "facts": [], "preferences": [], "conversations": [], 
                    "discoveries": [], "timeline": []
                }
                return

            # 安全地获取 facts
            facts = self.memories.get("facts", [])
            if not isinstance(facts, list):
                facts = []

            for fact in facts:
                if not isinstance(fact, dict):
                    continue

                keywords = fact.get("keywords", [])
                if not isinstance(keywords, list):
                    continue

                # 确保 keywords 中的元素是字符串
                keywords = [str(k) for k in keywords if k]

                for i in range(len(keywords)):
                    for j in range(i+1, len(keywords)):
                        self.association_graph[keywords[i]].add(keywords[j])
                        self.association_graph[keywords[j]].add(keywords[i])
        except Exception as e:
            print(f"构建关联图异常: {e}")

    def store_memory(self, memory_type, content, importance=0.5, context=None):
        """存储记忆"""
        memory_id = f"mem_{uuid.uuid4().hex[:8]}_{int(time.time() * 1000)}"

        memory_entry = {
            "id": memory_id,
            "type": memory_type,
            "content": content,
            "importance": importance,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None
        }

        # 确保 memories[memory_type] 是列表
        if memory_type not in self.memories:
            self.memories[memory_type] = []

        self.memories[memory_type].append(memory_entry)

        # 如果是事实记忆，更新关联图
        if memory_type == "facts" and isinstance(content, dict) and "keywords" in content:
            keywords = content["keywords"]
            if isinstance(keywords, list):
                keywords = [str(k) for k in keywords if k]
                for i in range(len(keywords)):
                    for j in range(i+1, len(keywords)):
                        self.association_graph[keywords[i]].add(keywords[j])
                        self.association_graph[keywords[j]].add(keywords[i])

        # 添加到时间线
        timeline_entry = {
            "memory_id": memory_id,
            "type": memory_type,
            "summary": str(content)[:50] if not isinstance(content, dict) else content.get("summary", str(content)[:50]),
            "timestamp": datetime.now().isoformat()
        }

        if "timeline" not in self.memories:
            self.memories["timeline"] = []
        self.memories["timeline"].append(timeline_entry)

        self._save_memories()
        return memory_id

    def retrieve_memories(self, query, memory_type=None, limit=5):
        """检索相关记忆"""
        memories_to_search = []

        if memory_type:
            memories_to_search = self.memories.get(memory_type, [])
        else:
            for mem_type, items in self.memories.items():
                if mem_type != "timeline" and isinstance(items, list):
                    memories_to_search.extend(items)

        # 简单关键词匹配
        relevant_memories = []
        query_words = set(str(query).lower().split())

        for memory in memories_to_search:
            if not isinstance(memory, dict):
                continue

            content = memory.get("content", {})
            content_str = json.dumps(content).lower()

            # 计算匹配度
            match_score = 0
            for word in query_words:
                if word in content_str:
                    match_score += 1

            # 考虑重要性
            importance_score = memory.get("importance", 0.5)

            # 考虑新鲜度
            freshness_score = self._calculate_freshness_score(memory)

            total_score = (match_score * 0.5 +
                          importance_score * 0.3 +
                          freshness_score * 0.2)

            if total_score > 0.2:
                relevant_memories.append((memory, total_score))

        # 按分数排序
        relevant_memories.sort(key=lambda x: x[1], reverse=True)

        # 更新访问记录
        for memory, _ in relevant_memories[:limit]:
            memory["access_count"] = memory.get("access_count", 0) + 1
            memory["last_accessed"] = datetime.now().isoformat()

        self._save_memories()
        return [mem[0] for mem in relevant_memories[:limit]]

    def _calculate_freshness_score(self, memory):
        """计算记忆新鲜度分数"""
        last_accessed = memory.get("last_accessed")
        if not last_accessed:
            return 0.5

        try:
            last_time = datetime.fromisoformat(last_accessed)
            days_passed = (datetime.now() - last_time).days

            if days_passed < 7:
                return 1.0
            elif days_passed < 30:
                return 1.0 - (days_passed - 7) * 0.9 / 23
            else:
                return 0.1
        except:
            return 0.5

    def find_associations(self, concept, depth=2):
        """查找概念关联"""
        if not hasattr(self, 'association_graph'):
            self.association_graph = defaultdict(set)

        visited = set()
        associations = set()

        def dfs(current_concept, current_depth):
            if current_depth > depth or current_concept in visited:
                return

            visited.add(current_concept)
            associations.add(current_concept)

            # 查找直接关联
            for neighbor in self.association_graph.get(str(current_concept), []):
                if neighbor not in visited:
                    dfs(neighbor, current_depth + 1)

        dfs(str(concept), 0)
        return list(associations - {str(concept)})

    def summarize_knowledge(self, topic):
        """总结某个话题的知识"""
        related_memories = self.retrieve_memories(topic, "facts")

        if not related_memories:
            return None

        facts = []
        for memory in related_memories[:3]:
            content = memory.get("content", {})
            if isinstance(content, dict):
                facts.append(content.get("fact", str(content)))
            else:
                facts.append(str(content))

        summary = {
            "topic": topic,
            "fact_count": len(related_memories),
            "key_facts": facts,
            "last_learned": related_memories[0].get("timestamp") if related_memories else None
        }
        return summary

    class HierarchicalMemory:
        """分层记忆系统"""

        def __init__(self):
            # 记忆层次
            self.sensory_buffer = []  # 感官缓冲（最近几秒）
            self.short_term = []  # 短期记忆（最近几分钟）
            self.long_term = []  # 长期记忆（几天到几周）
            self.procedural = {}  # 程序记忆（技能和习惯）

            # 记忆巩固参数
            self.consolidation_threshold = 0.7
            self.forgetting_curve = {}  # 遗忘曲线跟踪

        def consolidate_memory(self, memory):
            """记忆巩固：从短期记忆转移到长期记忆"""
            importance = self._calculate_importance(memory)
            if importance > self.consolidation_threshold:
                memory["strength"] = 1.0
                memory["consolidated"] = True
                self.long_term.append(memory)
                return True
            return False

        def retrieve_contextual(self, context, depth=3):
            """情境记忆检索"""
            relevant = []
            for memory in self.long_term:
                relevance = self._calculate_relevance(memory, context)
                if relevance > 0.3:
                    memory["last_retrieved"] = time.time()
                    memory["retrieval_count"] = memory.get("retrieval_count", 0) + 1
                    relevant.append((memory, relevance))

            relevant.sort(key=lambda x: x[1], reverse=True)
            return [mem[0] for mem in relevant[:depth]]

    def _save_memories(self):
        """保存记忆"""
        save_json(self.memory_file, self.memories)
