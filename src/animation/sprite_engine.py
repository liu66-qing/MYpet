"""精灵动画引擎"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

from src.animation.sprite_loader import SpriteLoader, AnimationConfig
from src.core.event_bus import EventBus, Events


class SpriteEngine(QLabel):
    animation_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loader: SpriteLoader | None = None
        self._current_anim: AnimationConfig | None = None
        self._current_frame = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)
        self._bus = EventBus()

    def set_loader(self, loader: SpriteLoader):
        self._loader = loader

    def play(self, animation_name: str):
        if self._loader is None:
            return
        anim = self._loader.get_animation(animation_name)
        if anim is None:
            return
        if self._current_anim and self._current_anim.name == animation_name:
            return
        self._current_anim = anim
        self._current_frame = 0
        self._show_frame()
        interval = int(1000 / anim.fps)
        self._timer.start(interval)

    def stop(self):
        self._timer.stop()

    def _next_frame(self):
        if not self._current_anim or not self._current_anim.frames:
            return
        self._current_frame += 1
        if self._current_frame >= len(self._current_anim.frames):
            if self._current_anim.loop:
                self._current_frame = 0
            else:
                self._timer.stop()
                name = self._current_anim.name
                next_anim = self._current_anim.next_animation
                self._bus.publish(Events.ANIMATION_FINISHED, name)
                self.animation_finished.emit(name)
                if next_anim and self._loader.get_animation(next_anim):
                    self.play(next_anim)
                return
        self._show_frame()

    def _show_frame(self):
        if self._current_anim and self._current_anim.frames:
            pixmap = self._current_anim.frames[self._current_frame]
            parent = self.parent()
            if parent:
                target_size = parent.size()
                pixmap = pixmap.scaled(
                    target_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            self.setPixmap(pixmap)
            self.setFixedSize(pixmap.size())
