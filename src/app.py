"""MYpet 应用入口"""
import sys
from PyQt6.QtWidgets import QApplication

from src.core.pet_window import PetWindow
from src.core.config_manager import ConfigManager
from src.core.event_bus import EventBus, Events
from src.core.state_machine import PetState
from src.ai.base_provider import AIProvider
from src.ai.openai_provider import OpenAIProvider
from src.ai.status_monitor import StatusMonitor
from src.monitor.socket_server import SocketServer


def create_provider(config: ConfigManager) -> AIProvider | None:
    provider_name = config.get("ai.provider", "openai")
    ai_config = {
        "api_key": config.get("ai.api_key", ""),
        "base_url": config.get("ai.base_url", "https://api.openai.com/v1"),
        "model": config.get("ai.model", "gpt-4o"),
    }
    if provider_name == "openai":
        return OpenAIProvider(ai_config)
    return None


CATEGORY_TO_STATE = {
    "error": PetState.ERROR,
    "success": PetState.HAPPY,
    "progress": PetState.CODING,
}


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = ConfigManager()
    provider = create_provider(config)
    bus = EventBus()

    window = PetWindow(config, provider)
    window.show()

    # 启动socket server监听终端消息
    socket_server = SocketServer()

    def on_socket_message(msg: dict):
        msg_type = msg.get("type", "")
        if msg_type == "terminal":
            category = msg.get("category", "")
            pet_state = CATEGORY_TO_STATE.get(category, PetState.IDLE)
            bus.publish(Events.TERMINAL_EVENT, {
                "category": category,
                "line": msg.get("line", ""),
                "pet_state": pet_state,
            })
        elif msg_type == "notify":
            bus.publish(Events.TERMINAL_NOTIFY, {
                "message": msg.get("message", ""),
                "category": msg.get("category", "info"),
            })
        elif msg_type == "state":
            state_map = {
                "idle": PetState.IDLE,
                "thinking": PetState.THINKING,
                "coding": PetState.CODING,
                "searching": PetState.SEARCHING,
                "happy": PetState.HAPPY,
                "sleeping": PetState.SLEEPING,
                "error": PetState.ERROR,
            }
            state = state_map.get(msg.get("state", ""), PetState.IDLE)
            window.state_machine.transition_to(state)

    socket_server.message_received.connect(on_socket_message)
    socket_server.start()

    if provider and provider.is_connected:
        poll_interval = config.get("ai.monitor.poll_interval", 500)
        monitor = StatusMonitor(provider, poll_interval)
        monitor.start()

    sys.exit(app.exec())
