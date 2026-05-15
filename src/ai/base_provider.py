"""AI服务提供者抽象基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator


class AIStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    GENERATING = "generating"
    TOOL_CALLING = "tool_calling"
    SEARCHING = "searching"
    ERROR = "error"


@dataclass
class AIStatusUpdate:
    status: AIStatus
    message: str = ""
    progress: float = -1
    metadata: dict = field(default_factory=dict)


@dataclass
class ChatMessage:
    role: str
    content: str


class AIProvider(ABC):
    @abstractmethod
    async def send_message(self, message: str, history: list[ChatMessage]) -> str: ...

    @abstractmethod
    async def stream_message(self, message: str, history: list[ChatMessage]) -> AsyncGenerator[str, None]: ...

    @abstractmethod
    def get_status(self) -> AIStatusUpdate: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def is_connected(self) -> bool: ...
