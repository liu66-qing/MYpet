"""OpenAI兼容API Provider"""
import asyncio
from typing import AsyncGenerator

from openai import AsyncOpenAI

from src.ai.base_provider import AIProvider, AIStatus, AIStatusUpdate, ChatMessage


class OpenAIProvider(AIProvider):
    def __init__(self, config: dict):
        self._api_key = config.get("api_key", "")
        self._base_url = config.get("base_url", "https://api.openai.com/v1")
        self._model = config.get("model", "gpt-4o")
        self._client: AsyncOpenAI | None = None
        self._status = AIStatusUpdate(status=AIStatus.IDLE)
        self._connected = False

        if self._api_key:
            self._client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
            self._connected = True

    @property
    def name(self) -> str:
        return "OpenAI"

    @property
    def is_connected(self) -> bool:
        return self._connected

    def get_status(self) -> AIStatusUpdate:
        return self._status

    async def send_message(self, message: str, history: list[ChatMessage]) -> str:
        if not self._client:
            self._status = AIStatusUpdate(status=AIStatus.ERROR, message="未配置API Key")
            return "错误：未配置API Key，请在config.yaml中设置"

        self._status = AIStatusUpdate(status=AIStatus.THINKING, message="思考中...")
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({"role": "user", "content": message})

        try:
            self._status = AIStatusUpdate(status=AIStatus.GENERATING, message="生成回复中...")
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
            )
            self._status = AIStatusUpdate(status=AIStatus.IDLE)
            return response.choices[0].message.content or ""
        except Exception as e:
            self._status = AIStatusUpdate(status=AIStatus.ERROR, message=str(e))
            return f"错误：{e}"

    async def stream_message(self, message: str, history: list[ChatMessage]) -> AsyncGenerator[str, None]:
        if not self._client:
            self._status = AIStatusUpdate(status=AIStatus.ERROR, message="未配置API Key")
            yield "错误：未配置API Key"
            return

        self._status = AIStatusUpdate(status=AIStatus.THINKING, message="思考中...")
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({"role": "user", "content": message})

        try:
            self._status = AIStatusUpdate(status=AIStatus.GENERATING, message="生成中...")
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
            self._status = AIStatusUpdate(status=AIStatus.IDLE)
        except Exception as e:
            self._status = AIStatusUpdate(status=AIStatus.ERROR, message=str(e))
            yield f"错误：{e}"
