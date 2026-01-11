"""更新后的主窗口，集成Agent系统"""
import time
from PyQt5.QtWidgets import (QWidget, QMenu, QAction, QSystemTrayIcon,
                             QApplication, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QPainter
import os
import logging

from core.config import IMAGES_DIR
from ui.chat_dialog import ChatDialog
from services.interaction_service import InteractionService
from core.agent.study_pet_agent import StudyPetAgent
from ui.agent_monitor import AgentMonitorDialog
from ui.emotion_display import EmotionDisplay


class PetWindow(QWidget):
    """桌宠主窗口 - 集成Agent系统"""

    def __init__(self, agent: StudyPetAgent = None, interaction_service: InteractionService = None):
        super().__init__()

        # 初始化服务和Agent
        self.agent = agent or StudyPetAgent(name="小桌")
        self.interaction_service = interaction_service or InteractionService(self.agent)

        # UI组件
        self.chat_dialog = None
        self.agent_monitor = None
        self.emotion_display = None

        # 状态变量
        self.current_emotion = "idle"
        self.is_monitoring = False

        # 初始化
        self._init_resources()
        self._init_ui()
        self._init_timer()
        self._init_tray()

        self.logger = logging.getLogger(__name__)
        self.logger.info("桌宠窗口初始化完成")

    def _init_resources(self):
        """初始化资源"""
        # 加载设置
        from core.config import load_settings
        self.settings = load_settings()

        # 图片尺寸
        self.pet_size = self.settings.get("pet_size", 100)
        self.default_pos = (
            self.settings.get("default_position_x", 500),
            self.settings.get("default_position_y", 300)
        )

    def _init_ui(self):
        """初始化界面"""
        # 窗口设置
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.pet_size, self.pet_size)
        self.move(*self.default_pos)

        # 加载桌宠图片
        self._load_emotion_image("idle")

        # 创建情感显示组件
        self.emotion_display = EmotionDisplay(self)
        self.emotion_display.move(10, 10)

        # 拖拽相关
        self.drag_pos = None

        # 定时更新情感显示
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_emotion_display)
        self.update_timer.start(1000)  # 每秒更新一次

    def _init_timer(self):
        """初始化定时器"""
        # 主动推送定时器
        self.push_timer = QTimer()
        self.push_timer.timeout.connect(self._active_push)
        push_interval = self.settings.get("active_push_interval", 3600) * 1000
        self.push_timer.start(push_interval)

        # 状态更新定时器
        self.state_timer = QTimer()
        self.state_timer.timeout.connect(self._update_agent_state)
        self.state_timer.start(60000)  # 每分钟更新一次

    def _init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(self.current_pixmap))
        self.tray_icon.setToolTip("智能学习桌宠")

        # 创建托盘菜单
        tray_menu = QMenu()

        chat_action = QAction("聊天", self)
        chat_action.triggered.connect(self.open_chat_dialog)

        monitor_action = QAction("监控面板", self)
        monitor_action.triggered.connect(self.open_agent_monitor)

        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)

        tray_menu.addAction(chat_action)
        tray_menu.addAction(monitor_action)
        tray_menu.addSeparator()
        tray_menu.addAction(settings_action)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # 托盘点击事件
        self.tray_icon.activated.connect(self._on_tray_activated)

    def _load_emotion_image(self, emotion: str):
        """加载情感对应的图片"""
        img_name = f"{emotion}.png"
        img_path = os.path.join(IMAGES_DIR, img_name)

        if os.path.exists(img_path):
            self.current_pixmap = QPixmap(img_path).scaled(
                self.pet_size, self.pet_size,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        else:
            # 回退到默认
            self.current_pixmap = QPixmap(self.pet_size, self.pet_size)
            self.current_pixmap.fill(Qt.blue)

        self.current_emotion = emotion
        self.setMask(self.current_pixmap.mask())
        self.update()

    def paintEvent(self, event):
        """绘制桌宠"""
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.end()

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)

        chat_action = QAction("聊天", self)
        chat_action.triggered.connect(self.open_chat_dialog)

        monitor_action = QAction("监控面板", self)
        monitor_action.triggered.connect(self.open_agent_monitor)

        reflect_action = QAction("自我反思", self)
        reflect_action.triggered.connect(self._trigger_agent_reflection)

        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)

        menu.addAction(chat_action)
        menu.addAction(monitor_action)
        menu.addAction(reflect_action)
        menu.addSeparator()
        menu.addAction(settings_action)
        menu.addAction(exit_action)

        menu.exec_(pos)

    def open_chat_dialog(self):
        """打开聊天对话框"""
        if not self.chat_dialog or not self.chat_dialog.isVisible():
            self.chat_dialog = ChatDialog(self, self.interaction_service)
            self.chat_dialog.send_message.connect(self._handle_user_message)
            self.chat_dialog.submit_rating.connect(self._handle_rating)

            # 定位聊天窗口
            pet_pos = self.pos()
            self.chat_dialog.move(pet_pos.x() + 100, pet_pos.y())
            self.chat_dialog.show()

            # 切换到聊天表情
            self._load_emotion_image("chat")

    def open_agent_monitor(self):
        """打开Agent监控面板"""
        if not self.agent_monitor or not self.agent_monitor.isVisible():
            self.agent_monitor = AgentMonitorDialog(self, self.agent)
            self.agent_monitor.move(600, 100)
            self.agent_monitor.show()

    def open_settings(self):
        """打开设置对话框"""
        from ui.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self)
        settings_dialog.settings_saved.connect(self._apply_settings)
        settings_dialog.exec_()

    def _handle_user_message(self, text: str):
        """处理用户消息"""
        try:
            # 获取Agent响应
            result = self.interaction_service.process_message(text)

            if result["success"]:
                # 更新聊天对话框
                if self.chat_dialog:
                    self.chat_dialog.add_agent_message(
                        result["response"],
                        result.get("conversation_id")
                    )

                # 更新情感状态
                emotion_state = self.agent.central_executive.emotion_system.get_state()
                dominant_emotion = emotion_state.get("dominant", "neutral")
                self._load_emotion_image(dominant_emotion)

                # 如果有建议，显示提示
                if result.get("suggestions"):
                    self._show_suggestion(result["suggestions"])

            else:
                # 处理错误
                self._show_error(result.get("error", "未知错误"))

        except Exception as e:
            self.logger.error(f"处理消息时出错: {e}", exc_info=True)
            self._show_error(f"处理失败: {str(e)}")

    def _handle_rating(self, conversation_id: str, rating: int):
        """处理评分"""
        try:
            success = self.interaction_service.rate_conversation(
                conversation_id, rating
            )
            if success:
                # 根据评分更新情感
                if rating >= 4:
                    self._load_emotion_image("happy")
                    QTimer.singleShot(3000, lambda: self._load_emotion_image("idle"))
                elif rating <= 2:
                    self._load_emotion_image("sad")
                    QTimer.singleShot(3000, lambda: self._load_emotion_image("idle"))

                # 显示确认消息
                self._show_message("评分已记录，谢谢反馈！")
        except Exception as e:
            self.logger.error(f"处理评分时出错: {e}")

    def _trigger_agent_reflection(self):
        """触发Agent自我反思"""
        try:
            reflection = self.agent.reflect()

            # 显示反思结果
            message = "我进行了自我反思：\n"
            for insight in reflection.get("insights", []):
                message += f"• {insight}\n"

            QMessageBox.information(self, "Agent反思", message)

        except Exception as e:
            self.logger.error(f"触发反思时出错: {e}")

    def _active_push(self):
        """主动推送内容"""
        if self.settings.get("enable_active_push", True):
            try:
                # 根据Agent状态生成推送内容
                agent_status = self.agent.get_status()

                if agent_status["state"]["curiosity"] > 0.7:
                    message = "我很好奇，今天有什么想学的吗？🤔"
                elif agent_status["state"]["relationship_level"] > 0.5:
                    message = "嗨，朋友！想聊点什么吗？😊"
                else:
                    message = "今天也要好好学习哦！💪"

                QMessageBox.information(self, "桌宠提醒", message)

            except Exception as e:
                self.logger.error(f"主动推送失败: {e}")

    def _update_agent_state(self):
        """更新Agent状态"""
        # 触发Agent自我状态检查
        self.agent._update_state()

        # 更新情感显示
        self._update_emotion_display()

    def _update_emotion_display(self):
        """更新情感显示"""
        if self.emotion_display:
            emotion_state = self.agent.central_executive.emotion_system.get_state()
            self.emotion_display.update_emotions(emotion_state)

    def _apply_settings(self, new_settings: dict):
        """应用新设置"""
        self.settings = new_settings

        # 更新界面
        self.pet_size = new_settings.get("pet_size", 100)
        self.setFixedSize(self.pet_size, self.pet_size)

        # 重新加载图片
        self._load_emotion_image(self.current_emotion)

        # 更新定时器
        push_interval = new_settings.get("active_push_interval", 3600) * 1000
        self.push_timer.setInterval(push_interval)

        self.logger.info("设置已应用")

    def _on_tray_activated(self, reason):
        """托盘激活事件"""
        if reason == QSystemTrayIcon.Trigger:
            self.open_chat_dialog()

    def _show_message(self, message: str):
        """显示消息"""
        if self.chat_dialog and self.chat_dialog.isVisible():
            self.chat_dialog.add_agent_message(message, None)
        else:
            QMessageBox.information(self, "桌宠消息", message)

    def _show_suggestion(self, suggestion: str):
        """显示建议"""
        QMessageBox.information(self, "桌宠建议", suggestion)

    def _show_error(self, error: str):
        """显示错误"""
        QMessageBox.warning(self, "出错啦", f"抱歉，出现了错误：\n{error}")

    def closeEvent(self, event):
        """关闭事件"""
        # 停止定时器
        self.push_timer.stop()
        self.state_timer.stop()
        self.update_timer.stop()

        # 保存状态
        try:
            self._save_agent_state()
        except Exception as e:
            self.logger.error(f"保存状态失败: {e}")

        # 隐藏托盘
        self.tray_icon.hide()

        # 退出应用
        QApplication.instance().quit()
        event.accept()

    def _save_agent_state(self):
        """保存Agent状态"""
        from utils.file_helper import save_json
        from core.config import DATA_DIR

        # 保存Agent状态
        agent_state = self.agent.get_status()
        save_json(os.path.join(DATA_DIR, "agent_state.json"), agent_state)

        # 保存对话
        conversations = self.interaction_service.get_conversation_history()
        save_json(os.path.join(DATA_DIR, "conversations_backup.json"), conversations)

        self.logger.info("Agent状态已保存")