"""事件总线 - 发布/订阅模式解耦模块通信"""
from typing import Any, Callable


class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance

    def subscribe(self, event: str, callback: Callable):
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable):
        if event in self._subscribers:
            self._subscribers[event] = [
                cb for cb in self._subscribers[event] if cb != callback
            ]

    def publish(self, event: str, data: Any = None):
        for cb in self._subscribers.get(event, []):
            cb(data)


class Events:
    AI_STATE_CHANGED = "ai.state_changed"
    AI_MESSAGE_RECEIVED = "ai.message_received"
    PET_CLICKED = "pet.clicked"
    PET_DOUBLE_CLICKED = "pet.double_clicked"
    PET_DRAGGED = "pet.dragged"
    ANIMATION_FINISHED = "animation.finished"
    CHAT_USER_INPUT = "chat.user_input"
    CONFIG_UPDATED = "config.updated"
    STATE_CHANGED = "state.changed"
    TERMINAL_EVENT = "terminal.event"
    TERMINAL_NOTIFY = "terminal.notify"
