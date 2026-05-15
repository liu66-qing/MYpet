"""透明无边框主窗口 - 宠物容器"""
import os

from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QAction, QCursor

from src.core.config_manager import ConfigManager
from src.core.event_bus import EventBus, Events
from src.core.state_machine import StateMachine, PetState
from src.animation.sprite_engine import SpriteEngine
from src.animation.sprite_loader import SpriteLoader
from src.ai.base_provider import AIProvider


class PetWindow(QMainWindow):
    def __init__(self, config: ConfigManager, provider: AIProvider = None):
        super().__init__()
        self._config = config
        self._provider = provider
        self._bus = EventBus()
        self._state_machine = StateMachine()
        self._drag_pos: QPoint | None = None
        self._chat_window = None
        self._bubble = None

        self._setup_window()
        self._setup_animation()
        self._setup_tray()
        self._connect_events()
        self._position_window()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        size = self._config.get("pet.window.size", [128, 128])
        self.setFixedSize(size[0], size[1])

    def _setup_animation(self):
        self._sprite = SpriteEngine(self)
        self._sprite.move(0, 0)

        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sprite_set = self._config.get("pet.sprite_set", "default")
        sprite_dir = os.path.join(base, "assets", "sprites", sprite_set)
        manifest = os.path.join(sprite_dir, "manifest.json")

        self._loader = SpriteLoader(sprite_dir)
        if os.path.exists(manifest):
            self._loader.load_manifest(manifest)
            self._sprite.set_loader(self._loader)
            self._sprite.play("idle")
        else:
            self._create_placeholder()

    def _create_placeholder(self):
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
        from src.animation.sprite_loader import AnimationConfig

        frames = []
        for i in range(4):
            pix = QPixmap(128, 128)
            pix.fill(QColor(0, 0, 0, 0))
            painter = QPainter(pix)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            color = QColor(100, 180, 255, 200 + i * 10)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            offset = i * 2
            painter.drawEllipse(10 + offset, 20 + offset, 108 - offset * 2, 98 - offset * 2)
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Segoe UI Emoji", 28)
            painter.setFont(font)
            painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "\U0001f431")
            painter.end()
            frames.append(pix)

        anim = AnimationConfig(name="idle", frames=frames, fps=4, loop=True)
        self._loader._animations["idle"] = anim
        self._sprite.set_loader(self._loader)
        self._sprite.play("idle")

    def _setup_tray(self):
        self._tray = QSystemTrayIcon(self)
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "assets", "icons", "tray.png"
        )
        if os.path.exists(icon_path):
            self._tray.setIcon(QIcon(icon_path))
        else:
            from PyQt6.QtGui import QPixmap, QPainter, QColor
            pix = QPixmap(32, 32)
            pix.fill(QColor(0, 0, 0, 0))
            p = QPainter(pix)
            p.setBrush(QColor(100, 180, 255))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(2, 2, 28, 28)
            p.end()
            self._tray.setIcon(QIcon(pix))

        menu = QMenu()
        show_action = QAction("显示/隐藏", self)
        show_action.triggered.connect(self._toggle_visibility)
        menu.addAction(show_action)

        chat_action = QAction("打开对话", self)
        chat_action.triggered.connect(self._open_chat)
        menu.addAction(chat_action)

        menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.setToolTip("MYpet - AI桌面宠物")
        self._tray.show()

    def _connect_events(self):
        self._bus.subscribe(Events.STATE_CHANGED, self._on_state_changed)
        self._bus.subscribe(Events.PET_DOUBLE_CLICKED, self._on_double_click)
        self._bus.subscribe(Events.AI_STATE_CHANGED, self._on_ai_state_changed)
        self._bus.subscribe(Events.TERMINAL_EVENT, self._on_terminal_event)
        self._bus.subscribe(Events.TERMINAL_NOTIFY, self._on_terminal_notify)

    def _on_state_changed(self, data):
        state_to_anim = {
            PetState.IDLE: "idle",
            PetState.THINKING: "thinking",
            PetState.CODING: "coding",
            PetState.SEARCHING: "searching",
            PetState.CHATTING: "chatting",
            PetState.HAPPY: "happy",
            PetState.SLEEPING: "sleeping",
            PetState.ERROR: "error",
        }
        new_state = data["to"]
        anim_name = state_to_anim.get(new_state, "idle")
        if self._loader.get_animation(anim_name):
            self._sprite.play(anim_name)
        else:
            self._sprite.play("idle")

    def _on_ai_state_changed(self, data):
        pet_state = data["pet_state"]
        self._state_machine.transition_to(pet_state)
        ai_status = data["ai_status"]
        if ai_status.message and self._bubble:
            self._bubble.show_message(ai_status.message, anchor=self)

    def _on_terminal_event(self, data):
        """终端关键词事件 → 切换状态 + 托盘通知"""
        pet_state = data.get("pet_state", PetState.IDLE)
        self._state_machine.transition_to(pet_state)
        category = data.get("category", "")
        line = data.get("line", "")
        # 系统托盘气泡通知
        icons = {"error": "❌", "success": "✅", "progress": "⏳"}
        icon = icons.get(category, "💬")
        title = {"error": "检测到错误", "success": "任务完成", "progress": "进度更新"}.get(category, "终端消息")
        self._tray.showMessage(f"{icon} {title}", line[:100], msecs=3000)

    def _on_terminal_notify(self, data):
        """手动通知 → 显示气泡"""
        message = data.get("message", "")
        self._state_machine.transition_to(PetState.HAPPY)
        self._tray.showMessage("💬 MYpet", message, msecs=5000)

    def _on_double_click(self, _=None):
        self._open_chat()

    def _open_chat(self):
        from src.interaction.chat_window import ChatWindow
        if self._chat_window is None:
            self._chat_window = ChatWindow(self._provider)
        self._chat_window.show()
        self._chat_window.raise_()
        self._chat_window.activateWindow()

    def _position_window(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            pos = self._config.get("pet.window.start_position", "bottom_right")
            if pos == "bottom_right":
                x = geo.right() - self.width() - 50
                y = geo.bottom() - self.height() - 50
            elif pos == "bottom_left":
                x = geo.left() + 50
                y = geo.bottom() - self.height() - 50
            else:
                x = geo.center().x() - self.width() // 2
                y = geo.bottom() - self.height() - 50
            self.move(x, y)

    def _toggle_visibility(self):
        self.setVisible(not self.isVisible())

    def _quit(self):
        from PyQt6.QtWidgets import QApplication
        self._tray.hide()
        QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            self._bus.publish(Events.PET_CLICKED)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self._bus.publish(Events.PET_DRAGGED)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._bus.publish(Events.PET_DOUBLE_CLICKED)

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        chat_action = QAction("打开对话", self)
        chat_action.triggered.connect(self._open_chat)
        menu.addAction(chat_action)

        states_menu = menu.addMenu("切换状态")
        for state in PetState:
            action = QAction(state.name, self)
            action.triggered.connect(
                lambda checked, s=state: self._state_machine.transition_to(s)
            )
            states_menu.addAction(action)

        menu.addSeparator()
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)
        menu.exec(QCursor.pos())

    @property
    def state_machine(self) -> StateMachine:
        return self._state_machine
