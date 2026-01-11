# 桌宠基础配置
import os

# 项目根路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 资源路径
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
KNOWLEDGE_PATH = os.path.join(RESOURCES_DIR, "knowledge.json")
# 数据路径
DATA_DIR = os.path.join(BASE_DIR, "data")
CHAT_HISTORY_PATH = os.path.join(DATA_DIR, "chat_history.json")
RATING_RECORD_PATH = os.path.join(DATA_DIR, "rating_record.json")
DIALOG_WEIGHTS_PATH = os.path.join(DATA_DIR, "dialog_weights.json")

# 桌宠窗口配置
PET_WIDTH = 100  # 桌宠宽度
PET_HEIGHT = 100  # 桌宠高度
PET_DEFAULT_POS = (500, 300)  # 桌宠默认位置

# 评分权重配置
HIGH_RATING_THRESHOLD = 4  # 高评分阈值（≥4星）
LOW_RATING_THRESHOLD = 2  # 低评分阈值（≤2星）
DEFAULT_WEIGHT = 1.0  # 默认权重
HIGH_WEIGHT = 2.0  # 高评分权重
LOW_WEIGHT = 0.2  # 低评分权重

# 定时推送配置
ACTIVE_PUSH_INTERVAL = 3600  # 主动推送间隔（秒），默认1小时

# 在 config.py 中添加：

# 探索系统配置
EXPLORATION_HISTORY_PATH = os.path.join(DATA_DIR, "exploration_history.json")
EXPLORATION_CONFIG_PATH = os.path.join(DATA_DIR, "exploration_config.json")
USER_INTERESTS_PATH = os.path.join(DATA_DIR, "user_interests.json")
EXPLORATION_MEMORY_PATH = os.path.join(DATA_DIR, "exploration_memory.json")

# 探索参数
EXPLORATION_INTERVAL = 10  # 探索间隔（秒），默认5分钟
EXPLORATION_SUCCESS_THRESHOLD = 0.6  # 探索成功率阈值
MAX_EXPLORATIONS_PER_DAY = 20  # 每天最大探索次数

# 设置文件路径
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")


def load_settings():
    """加载设置"""
    from utils.file_helper import load_json

    default_settings = {
        # 探索设置
        "exploration_rate": 0.3,
        "exploration_interval": 300,
        "max_explorations_per_day": 10,
        "curiosity_threshold": 0.7,
        "knowledge_coverage_target": 0.8,
        "topic_diversity_weight": 0.5,
        "learning_gap_weight": 0.3,
        "user_interest_weight": 0.2,
        "exploration_success_threshold": 0.6,
        "enable_exploration": True,

        # 学习设置
        "high_rating_threshold": 4,
        "low_rating_threshold": 2,
        "high_weight": 2.0,
        "default_weight": 1.0,
        "low_weight": 0.2,
        "active_push_interval": 3600,
        "enable_active_push": True,

        # 界面设置
        "pet_size": 100,
        "default_position_x": 500,
        "default_position_y": 300,
        "chat_window_width": 400,
        "chat_window_height": 500,
        "font_size": 10,
    }

    saved_settings = load_json(SETTINGS_PATH, {})

    # 合并设置，确保所有键都存在
    for key, value in default_settings.items():
        if key not in saved_settings:
            saved_settings[key] = value

    return saved_settings


def save_settings(settings):
    """保存设置"""
    from utils.file_helper import save_json
    return save_json(SETTINGS_PATH, settings)