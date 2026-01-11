from PyQt5.QtWidgets import (QDialog, QWidget, QHBoxLayout,
                             QLabel, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class RatingStar(QLabel):
    """星级按钮"""
    star_clicked = pyqtSignal(int)

    def __init__(self, star_level, parent=None):
        super().__init__(parent)
        self.star_level = star_level
        self.setFixedSize(25, 25)
        self.setFont(QFont("SimHei", 18))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color: #cccccc;")
        self.setText("★")
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        """鼠标悬浮高亮"""
        if self.styleSheet() == "color: #cccccc;":
            self.setStyleSheet("color: #ffcc00;")

    def leaveEvent(self, event):
        """鼠标离开恢复（未选中状态）"""
        if not self.styleSheet().startswith("color: #ffcc00; font-weight"):
            self.setStyleSheet("color: #cccccc;")

    def mousePressEvent(self, event):
        """点击星级"""
        self.star_clicked.emit(self.star_level)


class RatingPanel(QDialog):
    """评分面板（适配微信风格）"""
    rating_submitted = pyqtSignal(str, int)  # dialog_id, rating

    def __init__(self, dialog_id, parent=None):
        super().__init__(parent)
        self.dialog_id = dialog_id
        self.selected_rating = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("给对话评分")
        self.setFixedSize(180, 90)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")

        # 布局
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(10, 10, 10, 10)
        v_layout.setSpacing(10)

        # 标题
        title_label = QLabel("给这条回复打分～")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("SimHei", 10))

        # 星级
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignCenter)
        self.stars = []
        for i in range(1, 6):
            star = RatingStar(i)
            star.star_clicked.connect(self.on_star_clicked)
            h_layout.addWidget(star)
            self.stars.append(star)

        # 确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.setFixedHeight(25)
        confirm_btn.clicked.connect(self.on_confirm)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #0084ff;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #0066cc;
            }
        """)

        v_layout.addWidget(title_label)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(confirm_btn)
        self.setLayout(v_layout)

    def on_star_clicked(self, level):
        """选择星级（选中的星级高亮）"""
        self.selected_rating = level
        for i, star in enumerate(self.stars):
            if i < level:
                star.setStyleSheet("color: #ffcc00; font-weight: bold;")
            else:
                star.setStyleSheet("color: #cccccc;")

    def on_confirm(self):
        """提交评分"""
        if self.selected_rating > 0:
            self.rating_submitted.emit(self.dialog_id, self.selected_rating)
            self.close()