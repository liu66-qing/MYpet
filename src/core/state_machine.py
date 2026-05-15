"""宠物状态机"""
from enum import Enum, auto
from typing import Callable

from src.core.event_bus import EventBus, Events


class PetState(Enum):
    IDLE = auto()
    THINKING = auto()
    CODING = auto()
    SEARCHING = auto()
    CHATTING = auto()
    HAPPY = auto()
    SLEEPING = auto()
    ERROR = auto()


class StateMachine:
    def __init__(self):
        self._state = PetState.IDLE
        self._on_enter: dict[PetState, list[Callable]] = {}
        self._on_exit: dict[PetState, list[Callable]] = {}
        self._bus = EventBus()

    @property
    def current_state(self) -> PetState:
        return self._state

    def on_enter(self, state: PetState, callback: Callable):
        self._on_enter.setdefault(state, []).append(callback)

    def on_exit(self, state: PetState, callback: Callable):
        self._on_exit.setdefault(state, []).append(callback)

    def transition_to(self, new_state: PetState):
        if new_state == self._state:
            return
        old_state = self._state
        for cb in self._on_exit.get(old_state, []):
            cb(old_state)
        self._state = new_state
        for cb in self._on_enter.get(new_state, []):
            cb(new_state)
        self._bus.publish(Events.STATE_CHANGED, {
            "from": old_state,
            "to": new_state,
        })
