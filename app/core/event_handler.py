from openai import AssistantEventHandler
from typing import Callable, Any
import json

class ChatEventHandler(AssistantEventHandler):
    def __init__(self, send_func: Callable[[dict], Any]):
        self.send_func = send_func
        self.full_response = ""

    async def on_text_created(self, text: str) -> None:
        await self.send_func({"type": "start", "content": ""})

    async def on_text_delta(self, delta: str, snapshot: str) -> None:
        self.full_response += delta
        await self.send_func({"type": "stream", "content": delta})

    async def on_tool_call_created(self, tool_call: Any) -> None:
        await self.send_func({"type": "tool_call", "content": str(tool_call)})

    async def on_tool_call_delta(self, delta: Any, snapshot: Any) -> None:
        await self.send_func({"type": "tool_call_delta", "content": str(delta)})

    async def on_run_completed(self) -> None:
        await self.send_func({"type": "end", "content": self.full_response})