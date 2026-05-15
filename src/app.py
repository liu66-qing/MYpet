"""MYpet 应用入口"""
import sys
from PyQt6.QtWidgets import QApplication

from src.core.pet_window import PetWindow
from src.core.config_manager import ConfigManager
from src.ai.base_provider import AIProvider
from src.ai.openai_provider import OpenAIProvider
from src.ai.status_monitor import StatusMonitor


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


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = ConfigManager()
    provider = create_provider(config)

    window = PetWindow(config, provider)
    window.show()

    if provider and provider.is_connected:
        poll_interval = config.get("ai.monitor.poll_interval", 500)
        monitor = StatusMonitor(provider, poll_interval)
        monitor.start()

    sys.exit(app.exec())
