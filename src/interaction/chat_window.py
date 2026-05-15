"""聊天窗口 - 与AI对话的完整界面"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QScrollArea, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from src.ai.base_provider import AIProvider, ChatMessage
from src.core.event_bus import EventBus, Events


class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    chunk_received = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, provider: AIProvider, message: str, history: list[ChatMessage]):
        super().__init__()
        self._provider = provider
        self._message = message
        self._history = history

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self._provider.send_message(self._message, self._history)
            )
            self.response_ready.emit(result)
        except Exception as e:
            self.response_ready.emit(f"错误：{e}")
        finally:
            loop.close()
            self.finished_signal.emit()


class ChatWindow(QWidget):
    def __init__(self, provider: AIProvider = None):
        super().__init__()
        self._provider = provider
        self._history: list[ChatMessage] = []
        self._worker: AIWorker | None = None
        self._bus = EventBus()
        self._setup_ui()

    def set_provider(self, provider: AIProvider):
        self._provider = provider

    def _setup_ui(self):
        self.setWindowTitle("MYpet - AI对话")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QWidget { background-color: #f5f5f5; }
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #3a8eef; }
            QPushButton:disabled { background-color: #ccc; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # 标题
        title = QLabel("与AI对话")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 聊天记录
        self._chat_display = QTextEdit()
        self._chat_display.setReadOnly(True)
        layout.addWidget(self._chat_display, 1)

        # 输入区
        input_layout = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("输入消息...")
        self._input.returnPressed.connect(self._send)
        input_layout.addWidget(self._input, 1)

        self._send_btn = QPushButton("发送")
        self._send_btn.clicked.connect(self._send)
        input_layout.addWidget(self._send_btn)

        layout.addLayout(input_layout)

    def _send(self):
        text = self._input.text().strip()
        if not text:
            return
        if not self._provider:
            self._append_message("系统", "未配置AI服务，请在config.yaml中设置API Key")
            return

        self._input.clear()
        self._append_message("你", text)
        self._send_btn.setEnabled(False)

        self._history.append(ChatMessage(role="user", content=text))
        self._worker = AIWorker(self._provider, text, self._history.copy())
        self._worker.response_ready.connect(self._on_response)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_response(self, text: str):
        self._append_message("AI", text)
        self._history.append(ChatMessage(role="assistant", content=text))

    def _on_finished(self):
        self._send_btn.setEnabled(True)
        self._worker = None

    def _append_message(self, sender: str, text: str):
        color = "#4a9eff" if sender == "AI" else "#333"
        self._chat_display.append(
            f'<p><b style="color:{color}">{sender}:</b> {text}</p>'
        )
