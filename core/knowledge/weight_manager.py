# weight_manager.py
from core.config import (
    CHAT_HISTORY_PATH, RATING_RECORD_PATH, DIALOG_WEIGHTS_PATH,
    HIGH_RATING_THRESHOLD, LOW_RATING_THRESHOLD,
    DEFAULT_WEIGHT, HIGH_WEIGHT, LOW_WEIGHT
)
from utils.file_helper import load_json, save_json


class WeightManager:
    def __init__(self):
        # 加载设置
        self.settings = self._load_settings()

        # 初始化实例属性
        self.DEFAULT_WEIGHT = self.settings.get("default_weight", 1.0)
        self.HIGH_WEIGHT = self.settings.get("high_weight", 2.0)
        self.LOW_WEIGHT = self.settings.get("low_weight", 0.2)
        self.HIGH_RATING_THRESHOLD = self.settings.get("high_rating_threshold", 4)
        self.LOW_RATING_THRESHOLD = self.settings.get("low_rating_threshold", 2)

        # 初始化数据文件
        self._init_files()

    def _load_settings(self):
        """加载设置"""
        from core.config import load_settings
        return load_settings()

    def update_settings(self, new_settings):
        """更新设置"""
        self.settings = new_settings

        # 更新阈值和权重
        self.DEFAULT_WEIGHT = new_settings.get("default_weight", 1.0)
        self.HIGH_WEIGHT = new_settings.get("high_weight", 2.0)
        self.LOW_WEIGHT = new_settings.get("low_weight", 0.2)
        self.HIGH_RATING_THRESHOLD = new_settings.get("high_rating_threshold", 4)
        self.LOW_RATING_THRESHOLD = new_settings.get("low_rating_threshold", 2)

        print("✅ 权重管理器设置已更新")

    def _init_files(self):
        """初始化权重相关文件"""
        from utils.file_helper import init_data_dir
        init_data_dir()

        if not load_json(CHAT_HISTORY_PATH):
            save_json(CHAT_HISTORY_PATH, [])
        if not load_json(RATING_RECORD_PATH):
            save_json(RATING_RECORD_PATH, [])
        if not load_json(DIALOG_WEIGHTS_PATH):
            save_json(DIALOG_WEIGHTS_PATH, {})

    def calculate_weight(self, rating):
        """根据评分计算权重"""
        if rating >= HIGH_RATING_THRESHOLD:
            return self.HIGH_WEIGHT
        elif LOW_RATING_THRESHOLD < rating < HIGH_RATING_THRESHOLD:
            return self.DEFAULT_WEIGHT
        else:
            return self.LOW_WEIGHT

    def update_dialog_weight(self, dialog_id, rating):
        """更新单条对话的权重（添加异常捕获）"""
        try:
            # 1. 计算新权重
            new_weight = self.calculate_weight(rating)

            # 2. 首先获取这次对话对应的学习内容ID
            chat_history = load_json(CHAT_HISTORY_PATH, [])
            related_dialog_id = None

            for item in chat_history:
                if item.get("dialog_id") == dialog_id:
                    related_dialog_id = item.get("related_dialog_id")
                    # 更新聊天记录中的评分和权重
                    item["rating"] = rating
                    item["weight"] = new_weight
                    break

            # 3. 确定权重ID：如果有相关学习内容，使用学习内容ID，否则使用对话ID
            weight_id = related_dialog_id if related_dialog_id else dialog_id

            # 4. 更新权重文件（使用学习内容ID作为键）
            dialog_weights = load_json(DIALOG_WEIGHTS_PATH, {})
            dialog_weights[weight_id] = new_weight
            save_json(DIALOG_WEIGHTS_PATH, dialog_weights)

            # 5. 保存评分记录
            rating_record = load_json(RATING_RECORD_PATH, [])
            import time
            rating_record.append({
                "dialog_id": dialog_id,
                "related_dialog_id": related_dialog_id,  # 新增字段
                "weight_id": weight_id,  # 新增字段
                "rating": rating,
                "timestamp": int(time.time() * 1000)
            })
            save_json(RATING_RECORD_PATH, rating_record)

            return new_weight
        except Exception as e:
            print(f"更新权重异常：{e}")
            return self.DEFAULT_WEIGHT

    def get_dialog_weight(self, dialog_id):
        """获取单条对话的权重（优先使用学习内容ID）"""
        try:
            dialog_weights = load_json(DIALOG_WEIGHTS_PATH, {})
            # 首先尝试直接获取
            weight = dialog_weights.get(dialog_id)
            if weight is not None:
                return weight

            # 如果找不到，尝试查找这个对话ID是否在聊天记录中，并获取其相关学习内容ID
            chat_history = load_json(CHAT_HISTORY_PATH, [])
            for item in chat_history:
                if item.get("dialog_id") == dialog_id:
                    related_id = item.get("related_dialog_id")
                    if related_id:
                        return dialog_weights.get(related_id, self.DEFAULT_WEIGHT)

            return self.DEFAULT_WEIGHT
        except Exception as e:
            print(f"获取权重异常：{e}")
            return self.DEFAULT_WEIGHT