from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QScrollArea, QLabel,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

# 确保 RatingPanel 能正常导入（如果路径不对，需调整）
try:
    from ui.rating_panel import RatingPanel
except ImportError:
    # 兜底：如果导入失败，临时定义简化版 RatingPanel（避免闪退）
    class RatingPanel(QDialog):
        rating_submitted = pyqtSignal(str, int)

        def __init__(self, dialog_id, parent=None):
            super().__init__(parent)
            self.dialog_id = dialog_id
            self.selected_rating = 0
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle("评分")
            self.setFixedSize(180, 90)
            v_layout = QVBoxLayout()
            self.label = QLabel("请评分（1-5星）")
            self.label.setAlignment(Qt.AlignCenter)
            confirm_btn = QPushButton("确认")
            confirm_btn.clicked.connect(self.on_confirm)
            v_layout.addWidget(self.label)
            v_layout.addWidget(confirm_btn)
            self.setLayout(v_layout)

        def on_confirm(self):
            self.rating_submitted.emit(self.dialog_id, 3)  # 默认3星
            self.close()


class ChatBubble(QLabel):
    """微信风格聊天气泡 - 修复参数定义错误"""

    # 关键修复：显式定义 text、is_user 参数，parent 为可选参数
    def __init__(self, text, is_user, parent=None):
        super().__init__(parent)  # 调用父类构造方法
        self.is_user = is_user
        self.setText(text)
        self.setWordWrap(True)
        self.setFont(QFont("SimHei", 10))
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)  # 宽度自适应内容

        # 微信风格样式
        if is_user:
            self.setStyleSheet("""
                QLabel {
                    background-color: #DCF8C6;
                    color: black;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 0px;
                    border-bottom-left-radius: 10px;
                    border-bottom-right-radius: 10px;
                    padding: 8px 12px;
                    margin: 5px 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: white;
                    color: black;
                    border: 1px solid #eeeeee;
                    border-top-left-radius: 0px;
                    border-top-right-radius: 10px;
                    border-bottom-left-radius: 10px;
                    border-bottom-right-radius: 10px;
                    padding: 8px 12px;
                    margin: 5px 10px;
                }
            """)


class ChatDialog(QDialog):
    """微信风格聊天对话框 - 修复参数调用错误"""
    send_message = pyqtSignal(str)
    submit_rating = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.dialog_id_map = {}
        self.init_ui()
        self.move(600, 300)

    def init_ui(self):
        self.setWindowTitle("桌宠聊天")
        self.setFixedSize(400, 500)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # 聊天容器
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(8)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.chat_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #cccccc;
                border-radius: 4px;
            }
        """)

        # 输入区域
        input_widget = QWidget()
        input_widget.setStyleSheet("background-color: white; padding: 5px; border-radius: 5px;")
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(5, 5, 5, 5)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("输入消息（支持：问 你叫什么->答 小桌 | 加 单词 pear-梨）")
        self.input_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 15px;
                padding: 8px 15px;
                background-color: #f5f5f5;
            }
            QLineEdit:focus {
                border-color: #0084ff;
                outline: none;
            }
        """)

        send_btn = QPushButton("发送")
        send_btn.setFixedSize(60, 30)
        send_btn.clicked.connect(self.on_send)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0084ff;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0066cc;
            }
            QPushButton:disabled {
                background-color: #999999;
            }
        """)

        input_layout.addWidget(self.input_edit)
        input_layout.addSpacing(10)
        input_layout.addWidget(send_btn)

        main_layout.addWidget(scroll_area, stretch=1)
        main_layout.addSpacing(5)
        main_layout.addWidget(input_widget)
        self.setLayout(main_layout)

    def on_send(self):
        """发送消息"""
        text = self.input_edit.text().strip()
        if not text:
            return
        self.input_edit.clear()
        self.send_message.emit(text)
        self.add_message(text, is_user=True)

    def add_message(self, text, is_user, dialog_id=None):
        """添加消息 - 修复参数调用"""
        # 1. 创建水平布局
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignTop)
        h_layout.setSpacing(0)
        h_layout.setContentsMargins(0, 0, 0, 0)

        # 关键修复：调用 ChatBubble 时参数匹配（text, is_user）
        bubble = ChatBubble(text, is_user, self)  # 显式传入 parent=self，避免参数歧义

        # 2. 对齐控制
        if is_user:
            h_layout.addStretch()
            h_layout.addWidget(bubble)
        else:
            h_layout.addWidget(bubble)
            h_layout.addStretch()
            if dialog_id:
                self.dialog_id_map[bubble] = dialog_id
                # 评分按钮布局
                rating_layout = QHBoxLayout()
                rating_layout.setAlignment(Qt.AlignLeft)
                rating_layout.setContentsMargins(15, 0, 0, 0)
                rating_btn = QPushButton("评分")
                rating_btn.setFixedSize(50, 20)
                rating_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #0084ff;
                        border: none;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        color: #0066cc;
                    }
                """)
                rating_btn.clicked.connect(lambda: self.show_rating_panel(dialog_id))
                rating_layout.addWidget(rating_btn)

                self.chat_layout.addLayout(h_layout)
                self.chat_layout.addLayout(rating_layout)
                self._scroll_to_bottom()
                return

        self.chat_layout.addLayout(h_layout)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """强制滚动到底部"""
        self.chat_container.adjustSize()
        QTimer.singleShot(10, self._do_scroll)

    def _do_scroll(self):
        """执行滚动"""
        scroll_area = self.findChild(QScrollArea)
        if scroll_area:
            scroll_bar = scroll_area.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

    def show_rating_panel(self, dialog_id):
        """显示评分面板"""
        self.rating_panel = RatingPanel(dialog_id, self)
        self.rating_panel.rating_submitted.connect(self.on_rating_submitted)
        self.rating_panel.exec_()

    def on_rating_submitted(self, dialog_id, rating):
        """评分提交"""
        self.submit_rating.emit(dialog_id, rating)
        self.add_message(f"✅ 评分成功！你给这条对话打了{rating}星～", is_user=False)

    def closeEvent(self, event):
        """关闭事件"""
        if self.parent():
            self.parent().raise_()
        event.accept()