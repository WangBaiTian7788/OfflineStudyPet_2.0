"""
设置对话框：允许用户调整探索系统参数
"""
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSlider, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QPushButton, QFormLayout,
                             QTabWidget, QCheckBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utils.file_helper import load_json, save_json
import json
import os


class SettingsSlider(QWidget):
    """带标签和值的滑块控件"""
    value_changed = pyqtSignal(float)

    def __init__(self, label, min_val, max_val, step, default_val, parent=None, tooltip=""):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.default_val = default_val
        self.tooltip_text = tooltip

        self.init_ui(label)

    def init_ui(self, label):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 标签和当前值
        top_layout = QHBoxLayout()
        self.label = QLabel(label)
        self.label.setFont(QFont("SimHei", 10))
        self.value_label = QLabel("0.0")
        self.value_label.setFont(QFont("SimHei", 10))
        self.value_label.setMinimumWidth(40)

        # 设置工具提示（如果有）
        if self.tooltip_text:
            self.label.setToolTip(self.tooltip_text)
            self.value_label.setToolTip(self.tooltip_text)

        top_layout.addWidget(self.label)
        top_layout.addStretch()
        top_layout.addWidget(self.value_label)

        # 滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(self.min_val / self.step))
        self.slider.setMaximum(int(self.max_val / self.step))
        self.slider.setValue(int(self.default_val / self.step))
        self.slider.valueChanged.connect(self.on_slider_changed)

        # 设置滑块的工具提示
        if self.tooltip_text:
            self.slider.setToolTip(self.tooltip_text)

        # 范围标签
        range_layout = QHBoxLayout()
        min_label = QLabel(f"{self.min_val:.1f}")
        min_label.setFont(QFont("SimHei", 8))
        max_label = QLabel(f"{self.max_val:.1f}")
        max_label.setFont(QFont("SimHei", 8))

        range_layout.addWidget(min_label)
        range_layout.addStretch()
        range_layout.addWidget(max_label)

        layout.addLayout(top_layout)
        layout.addWidget(self.slider)
        layout.addLayout(range_layout)

        self.setLayout(layout)

        # 更新初始值
        self.update_value_label(self.default_val)

    def on_slider_changed(self, value):
        """滑块值改变"""
        actual_value = value * self.step
        self.update_value_label(actual_value)
        self.value_changed.emit(actual_value)

    def update_value_label(self, value):
        """更新值标签"""
        if self.step < 0.1:
            self.value_label.setText(f"{value:.2f}")
        else:
            self.value_label.setText(f"{value:.1f}")

    def get_value(self):
        """获取当前值"""
        return self.slider.value() * self.step

    def set_value(self, value):
        """设置值"""
        slider_value = int(value / self.step)
        self.slider.setValue(slider_value)
        self.update_value_label(value)


class SettingsDialog(QDialog):
    """设置对话框"""
    settings_saved = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_file = "data/settings.json"
        self.current_settings = self.load_settings()
        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("桌宠设置")
        self.setFixedSize(600, 700)

        # 存储控件引用 - 必须在这里初始化
        self.settings_widgets = {}

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 创建选项卡
        tab_widget = QTabWidget()

        # 探索设置选项卡
        exploration_tab = self.create_exploration_tab()
        tab_widget.addTab(exploration_tab, "探索设置")

        # 学习设置选项卡
        learning_tab = self.create_learning_tab()
        tab_widget.addTab(learning_tab, "学习设置")

        # 界面设置选项卡
        interface_tab = self.create_interface_tab()
        tab_widget.addTab(interface_tab, "界面设置")

        # 按钮
        button_layout = QHBoxLayout()

        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0084ff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0066cc;
            }
        """)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #aaaaaa;
            }
        """)

        reset_btn = QPushButton("恢复默认")
        reset_btn.clicked.connect(self.reset_to_default)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9500;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e68500;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        main_layout.addWidget(tab_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def create_exploration_tab(self):
        """创建探索设置选项卡"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 探索频率设置
        exploration_group = QGroupBox("探索频率设置")
        exploration_group.setFont(QFont("SimHei", 11, QFont.Bold))
        exploration_layout = QFormLayout()

        # 探索概率
        self.exploration_rate_slider = SettingsSlider(
            "探索概率", 0.0, 1.0, 0.05, 0.3,
            tooltip="桌宠发起探索的概率，0表示从不探索，1表示总是探索"
        )
        exploration_layout.addRow("探索概率:", self.exploration_rate_slider)
        self.settings_widgets["exploration_rate"] = self.exploration_rate_slider

        # 探索间隔（秒）
        self.exploration_interval_spin = QSpinBox()
        self.exploration_interval_spin.setRange(30, 3600)
        self.exploration_interval_spin.setSingleStep(30)
        self.exploration_interval_spin.setValue(300)
        self.exploration_interval_spin.setSuffix(" 秒")
        exploration_layout.addRow("探索间隔:", self.exploration_interval_spin)
        self.settings_widgets["exploration_interval"] = self.exploration_interval_spin

        # 每天最大探索次数
        self.max_explorations_spin = QSpinBox()
        self.max_explorations_spin.setRange(1, 100)
        self.max_explorations_spin.setValue(10)
        self.max_explorations_spin.setSuffix(" 次")
        exploration_layout.addRow("每日最大探索:", self.max_explorations_spin)
        self.settings_widgets["max_explorations_per_day"] = self.max_explorations_spin

        exploration_group.setLayout(exploration_layout)

        # 探索策略设置
        strategy_group = QGroupBox("探索策略设置")
        strategy_group.setFont(QFont("SimHei", 11, QFont.Bold))
        strategy_layout = QFormLayout()

        # 好奇心阈值
        self.curiosity_threshold_slider = SettingsSlider(
            "好奇心阈值", 0.0, 1.0, 0.05, 0.7,
            tooltip="好奇心水平阈值，高于此值会发起更多探索"
        )
        strategy_layout.addRow("好奇心阈值:", self.curiosity_threshold_slider)
        self.settings_widgets["curiosity_threshold"] = self.curiosity_threshold_slider

        # 知识覆盖率目标
        self.knowledge_coverage_slider = SettingsSlider(
            "知识覆盖率目标", 0.0, 1.0, 0.05, 0.8,
            tooltip="期望覆盖的知识比例，影响探索广度"
        )
        strategy_layout.addRow("知识覆盖率:", self.knowledge_coverage_slider)
        self.settings_widgets["knowledge_coverage_target"] = self.knowledge_coverage_slider

        strategy_group.setLayout(strategy_layout)

        # 探索权重设置
        weights_group = QGroupBox("探索权重设置")
        weights_group.setFont(QFont("SimHei", 11, QFont.Bold))
        weights_layout = QFormLayout()

        # 话题多样性权重
        self.topic_diversity_slider = SettingsSlider(
            "话题多样性", 0.0, 1.0, 0.05, 0.5,
            tooltip="探索不同话题的权重，越高越倾向于多样化"
        )
        weights_layout.addRow("话题多样性权重:", self.topic_diversity_slider)
        self.settings_widgets["topic_diversity_weight"] = self.topic_diversity_slider

        # 学习缺口权重
        self.learning_gap_slider = SettingsSlider(
            "学习缺口", 0.0, 1.0, 0.05, 0.3,
            tooltip="填补知识空白的权重，越高越关注薄弱环节"
        )
        weights_layout.addRow("学习缺口权重:", self.learning_gap_slider)
        self.settings_widgets["learning_gap_weight"] = self.learning_gap_slider

        # 用户兴趣权重
        self.user_interest_slider = SettingsSlider(
            "用户兴趣", 0.0, 1.0, 0.05, 0.2,
            tooltip="用户兴趣导向的权重，越高越关注用户喜好"
        )
        weights_layout.addRow("用户兴趣权重:", self.user_interest_slider)
        self.settings_widgets["user_interest_weight"] = self.user_interest_slider

        weights_group.setLayout(weights_layout)

        # 探索评估设置
        evaluation_group = QGroupBox("探索评估设置")
        evaluation_group.setFont(QFont("SimHei", 11, QFont.Bold))
        evaluation_layout = QFormLayout()

        # 成功阈值
        self.success_threshold_slider = SettingsSlider(
            "成功阈值", 0.0, 1.0, 0.05, 0.6,
            tooltip="探索成功率阈值，影响策略调整"
        )
        evaluation_layout.addRow("成功阈值:", self.success_threshold_slider)
        self.settings_widgets["exploration_success_threshold"] = self.success_threshold_slider

        # 启用探索
        self.enable_exploration_check = QCheckBox("启用探索功能")
        self.enable_exploration_check.setChecked(True)
        evaluation_layout.addRow(self.enable_exploration_check)
        self.settings_widgets["enable_exploration"] = self.enable_exploration_check

        evaluation_group.setLayout(evaluation_layout)

        # 添加所有组到布局
        layout.addWidget(exploration_group)
        layout.addWidget(strategy_group)
        layout.addWidget(weights_group)
        layout.addWidget(evaluation_group)
        layout.addStretch()

        scroll_area.setWidget(container)
        return scroll_area

    def create_learning_tab(self):
        """创建学习设置选项卡"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 学习权重设置
        weight_group = QGroupBox("评分权重设置")
        weight_group.setFont(QFont("SimHei", 11, QFont.Bold))
        weight_layout = QFormLayout()

        # 高评分阈值
        self.high_rating_spin = QSpinBox()
        self.high_rating_spin.setRange(1, 5)
        self.high_rating_spin.setValue(4)
        self.high_rating_spin.setSuffix(" 星及以上")
        weight_layout.addRow("高评分阈值:", self.high_rating_spin)
        self.settings_widgets["high_rating_threshold"] = self.high_rating_spin

        # 低评分阈值
        self.low_rating_spin = QSpinBox()
        self.low_rating_spin.setRange(1, 5)
        self.low_rating_spin.setValue(2)
        self.low_rating_spin.setSuffix(" 星及以下")
        weight_layout.addRow("低评分阈值:", self.low_rating_spin)
        self.settings_widgets["low_rating_threshold"] = self.low_rating_spin

        # 高权重
        self.high_weight_spin = QDoubleSpinBox()
        self.high_weight_spin.setRange(0.1, 10.0)
        self.high_weight_spin.setSingleStep(0.1)
        self.high_weight_spin.setValue(2.0)
        weight_layout.addRow("高评分权重:", self.high_weight_spin)
        self.settings_widgets["high_weight"] = self.high_weight_spin

        # 默认权重
        self.default_weight_spin = QDoubleSpinBox()
        self.default_weight_spin.setRange(0.1, 10.0)
        self.default_weight_spin.setSingleStep(0.1)
        self.default_weight_spin.setValue(1.0)
        weight_layout.addRow("默认权重:", self.default_weight_spin)
        self.settings_widgets["default_weight"] = self.default_weight_spin

        # 低权重
        self.low_weight_spin = QDoubleSpinBox()
        self.low_weight_spin.setRange(0.01, 1.0)
        self.low_weight_spin.setSingleStep(0.05)
        self.low_weight_spin.setValue(0.2)
        weight_layout.addRow("低评分权重:", self.low_weight_spin)
        self.settings_widgets["low_weight"] = self.low_weight_spin

        weight_group.setLayout(weight_layout)

        # 主动推送设置
        push_group = QGroupBox("主动推送设置")
        push_group.setFont(QFont("SimHei", 11, QFont.Bold))
        push_layout = QFormLayout()

        # 推送间隔
        self.push_interval_spin = QSpinBox()
        self.push_interval_spin.setRange(60, 86400)
        self.push_interval_spin.setSingleStep(300)
        self.push_interval_spin.setValue(3600)
        self.push_interval_spin.setSuffix(" 秒")
        push_layout.addRow("推送间隔:", self.push_interval_spin)
        self.settings_widgets["active_push_interval"] = self.push_interval_spin

        # 启用主动推送
        self.enable_push_check = QCheckBox("启用主动推送")
        self.enable_push_check.setChecked(True)
        push_layout.addRow(self.enable_push_check)
        self.settings_widgets["enable_active_push"] = self.enable_push_check

        push_group.setLayout(push_layout)

        # 学习策略设置
        strategy_group = QGroupBox("学习策略设置")
        strategy_group.setFont(QFont("SimHei", 11, QFont.Bold))
        strategy_layout = QFormLayout()

        # 难度调整步长
        self.difficulty_step_spin = QDoubleSpinBox()
        self.difficulty_step_spin.setRange(0.01, 0.2)
        self.difficulty_step_spin.setSingleStep(0.01)
        self.difficulty_step_spin.setValue(0.05)
        strategy_layout.addRow("难度调整步长:", self.difficulty_step_spin)
        self.settings_widgets["difficulty_adjustment_step"] = self.difficulty_step_spin

        # 最小难度
        self.min_difficulty_spin = QDoubleSpinBox()
        self.min_difficulty_spin.setRange(0.0, 0.5)
        self.min_difficulty_spin.setSingleStep(0.05)
        self.min_difficulty_spin.setValue(0.1)
        strategy_layout.addRow("最小难度:", self.min_difficulty_spin)
        self.settings_widgets["min_difficulty_level"] = self.min_difficulty_spin

        # 最大难度
        self.max_difficulty_spin = QDoubleSpinBox()
        self.max_difficulty_spin.setRange(0.5, 1.0)
        self.max_difficulty_spin.setSingleStep(0.05)
        self.max_difficulty_spin.setValue(1.0)
        strategy_layout.addRow("最大难度:", self.max_difficulty_spin)
        self.settings_widgets["max_difficulty_level"] = self.max_difficulty_spin

        strategy_group.setLayout(strategy_layout)

        # 添加所有组到布局
        layout.addWidget(weight_group)
        layout.addWidget(push_group)
        layout.addWidget(strategy_group)
        layout.addStretch()

        scroll_area.setWidget(container)
        return scroll_area

    def create_interface_tab(self):
        """创建界面设置选项卡"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 桌宠外观设置
        appearance_group = QGroupBox("桌宠外观")
        appearance_group.setFont(QFont("SimHei", 11, QFont.Bold))
        appearance_layout = QFormLayout()

        # 桌宠大小
        self.pet_size_spin = QSpinBox()
        self.pet_size_spin.setRange(50, 200)
        self.pet_size_spin.setSingleStep(10)
        self.pet_size_spin.setValue(100)
        self.pet_size_spin.setSuffix(" 像素")
        appearance_layout.addRow("桌宠大小:", self.pet_size_spin)
        self.settings_widgets["pet_size"] = self.pet_size_spin

        # 默认位置X
        self.default_x_spin = QSpinBox()
        self.default_x_spin.setRange(0, 1920)
        self.default_x_spin.setValue(500)
        appearance_layout.addRow("默认位置X:", self.default_x_spin)
        self.settings_widgets["default_position_x"] = self.default_x_spin

        # 默认位置Y
        self.default_y_spin = QSpinBox()
        self.default_y_spin.setRange(0, 1080)
        self.default_y_spin.setValue(300)
        appearance_layout.addRow("默认位置Y:", self.default_y_spin)
        self.settings_widgets["default_position_y"] = self.default_y_spin

        appearance_group.setLayout(appearance_layout)

        # 聊天窗口设置
        chat_group = QGroupBox("聊天窗口")
        chat_group.setFont(QFont("SimHei", 11, QFont.Bold))
        chat_layout = QFormLayout()

        # 聊天窗口宽度
        self.chat_width_spin = QSpinBox()
        self.chat_width_spin.setRange(300, 800)
        self.chat_width_spin.setSingleStep(10)
        self.chat_width_spin.setValue(400)
        self.chat_width_spin.setSuffix(" 像素")
        chat_layout.addRow("窗口宽度:", self.chat_width_spin)
        self.settings_widgets["chat_window_width"] = self.chat_width_spin

        # 聊天窗口高度
        self.chat_height_spin = QSpinBox()
        self.chat_height_spin.setRange(400, 1200)
        self.chat_height_spin.setSingleStep(10)
        self.chat_height_spin.setValue(500)
        self.chat_height_spin.setSuffix(" 像素")
        chat_layout.addRow("窗口高度:", self.chat_height_spin)
        self.settings_widgets["chat_window_height"] = self.chat_height_spin

        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix(" 像素")
        chat_layout.addRow("字体大小:", self.font_size_spin)
        self.settings_widgets["font_size"] = self.font_size_spin

        chat_group.setLayout(chat_layout)

        # 系统设置
        system_group = QGroupBox("系统设置")
        system_group.setFont(QFont("SimHei", 11, QFont.Bold))
        system_layout = QFormLayout()

        # 自动保存间隔
        self.auto_save_spin = QSpinBox()
        self.auto_save_spin.setRange(1, 60)
        self.auto_save_spin.setValue(5)
        self.auto_save_spin.setSuffix(" 分钟")
        system_layout.addRow("自动保存间隔:", self.auto_save_spin)
        self.settings_widgets["auto_save_interval"] = self.auto_save_spin

        # 显示调试信息
        self.show_debug_check = QCheckBox("显示调试信息")
        self.show_debug_check.setChecked(False)
        system_layout.addRow(self.show_debug_check)
        self.settings_widgets["show_debug_info"] = self.show_debug_check

        # 启用系统托盘
        self.enable_tray_check = QCheckBox("启用系统托盘")
        self.enable_tray_check.setChecked(True)
        system_layout.addRow(self.enable_tray_check)
        self.settings_widgets["enable_system_tray"] = self.enable_tray_check

        system_group.setLayout(system_layout)

        # 添加所有组到布局
        layout.addWidget(appearance_group)
        layout.addWidget(chat_group)
        layout.addWidget(system_group)
        layout.addStretch()

        scroll_area.setWidget(container)
        return scroll_area

    def load_settings(self):
        """加载设置"""
        default_settings = self.get_default_settings()

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved_settings = json.load(f)
                    # 合并设置（确保有默认值）
                    for key, value in default_settings.items():
                        if key not in saved_settings:
                            saved_settings[key] = value
                    return saved_settings
            except:
                return default_settings
        else:
            return default_settings

    def get_default_settings(self):
        """获取默认设置"""
        return {
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
            "difficulty_adjustment_step": 0.05,
            "min_difficulty_level": 0.1,
            "max_difficulty_level": 1.0,

            # 界面设置
            "pet_size": 100,
            "default_position_x": 500,
            "default_position_y": 300,
            "chat_window_width": 400,
            "chat_window_height": 500,
            "font_size": 10,
            "auto_save_interval": 5,
            "show_debug_info": False,
            "enable_system_tray": True
        }

    def load_current_settings(self):
        """加载当前设置到UI"""
        for key, widget in self.settings_widgets.items():
            if key in self.current_settings:
                value = self.current_settings[key]

                if isinstance(widget, SettingsSlider):
                    widget.set_value(value)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(value)
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(value)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value)

    def get_current_settings(self):
        """从UI获取当前设置"""
        settings = {}

        for key, widget in self.settings_widgets.items():
            if isinstance(widget, SettingsSlider):
                settings[key] = widget.get_value()
            elif isinstance(widget, QSpinBox):
                settings[key] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                settings[key] = widget.value()
            elif isinstance(widget, QCheckBox):
                settings[key] = widget.isChecked()

        return settings

    def save_settings(self):
        """保存设置"""
        # 获取当前设置
        new_settings = self.get_current_settings()

        # 验证设置
        if not self.validate_settings(new_settings):
            return

        # 保存到文件
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(new_settings, f, ensure_ascii=False, indent=4)

            # 更新当前设置
            self.current_settings = new_settings

            # 发射信号
            self.settings_saved.emit(new_settings)

            # 关闭对话框
            self.close()

            print("✅ 设置保存成功")

        except Exception as e:
            print(f"❌ 保存设置失败: {e}")

    def validate_settings(self, settings):
        """验证设置"""
        errors = []

        # 检查权重总和
        weights_sum = (
                settings.get("topic_diversity_weight", 0) +
                settings.get("learning_gap_weight", 0) +
                settings.get("user_interest_weight", 0)
        )

        if weights_sum == 0:
            errors.append("探索权重总和不能为0")
        elif weights_sum > 1.5:
            errors.append("探索权重总和过大，建议在0.5-1.5之间")

        # 检查探索概率
        exploration_rate = settings.get("exploration_rate", 0)
        if exploration_rate < 0 or exploration_rate > 1:
            errors.append("探索概率必须在0到1之间")

        # 检查探索间隔
        interval = settings.get("exploration_interval", 0)
        if interval < 10:
            errors.append("探索间隔不能小于10秒")

        # 如果有错误，显示提示
        if errors:
            error_msg = "设置验证失败：\n• " + "\n• ".join(errors)
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "设置验证失败", error_msg)
            return False

        return True

    def reset_to_default(self):
        """恢复到默认设置"""
        from PyQt5.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "恢复默认设置",
            "确定要恢复所有设置为默认值吗？当前设置将丢失。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            default_settings = self.get_default_settings()
            self.current_settings = default_settings
            self.load_current_settings()
            print("✅ 已恢复默认设置")