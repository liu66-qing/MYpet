"""AI状态监控器"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from src.ai.base_provider import AIProvider, AIStatus, AIStatusUpdate
from src.core.event_bus import EventBus, Events
from src.core.state_machine import PetState


STATUS_TO_PET_STATE = {
    AIStatus.IDLE: PetState.IDLE,
    AIStatus.THINKING: PetState.THINKING,
    AIStatus.GENERATING: PetState.CODING,
    AIStatus.TOOL_CALLING: PetState.SEARCHING,
    AIStatus.SEARCHING: PetState.SEARCHING,
    AIStatus.ERROR: PetState.IDLE,
}


class StatusMonitor(QObject):
    status_changed = pyqtSignal(object)

    def __init__(self, provider: AIProvider, poll_interval_ms: int = 500):
        super().__init__()
        self._provider = provider
        self._last_status: AIStatus | None = None
        self._bus = EventBus()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self._timer.setInterval(poll_interval_ms)

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def _poll(self):
        update = self._provider.get_status()
        if update.status != self._last_status:
            self._last_status = update.status
            self.status_changed.emit(update)
            pet_state = STATUS_TO_PET_STATE.get(update.status, PetState.IDLE)
            self._bus.publish(Events.AI_STATE_CHANGED, {
                "ai_status": update,
                "pet_state": pet_state,
            })
