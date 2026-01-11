import json
import os

from PyQt5.QtCore import QTimer

from core import DATA_DIR


class ActivePushTimer:
    """主动推送定时器"""

    def __init__(self, callback):
        self.timer = QTimer()
        self.callback = callback

        # 加载初始间隔
        self.update_interval()

    def update_interval(self, seconds=None):
        """更新间隔"""
        if seconds is None:
            # 从设置加载
            from core import load_settings
            settings = load_settings()
            seconds = settings.get("active_push_interval", 3600)

        self.timer.setInterval(seconds * 1000)  # 秒转毫秒
        self.timer.timeout.connect(self.callback)

    def start(self):
        """启动定时器"""
        self.timer.start()

    def stop(self):
        """停止定时器"""
        self.timer.stop()

    def set_interval(self, seconds):
        """设置间隔（秒）"""
        self.timer.setInterval(seconds * 1000)

def init_data_dir():
    """初始化数据目录（不存在则创建）"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_json(file_path, default=None):
    """加载JSON文件，文件不存在返回默认值"""
    if default is None:
        default = {}
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载JSON文件失败 {file_path}：{e}")
        return default

def save_json(file_path, data):
    """保存数据到JSON文件"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存JSON文件失败 {file_path}：{e}")
        return False

def generate_dialog_id():
    """生成唯一对话ID"""
    import time
    return f"dia_{int(time.time() * 1000)}"