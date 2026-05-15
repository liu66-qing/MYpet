"""对话气泡 - 宠物头顶的状态/消息提示"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath


class ChatBubble(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 230);
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 8px 12px;
                color: #333;
            }
        """)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_message(self, text: str, duration_ms: int = 3000, anchor=None):
        self.setText(text)
        self.adjustSize()
        if anchor:
            x = anchor.x() + anchor.width() // 2 - self.width() // 2
            y = anchor.y() - self.height() - 10
            self.move(x, y)
        self.show()
        self._timer.start(duration_ms)
