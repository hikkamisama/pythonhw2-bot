from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import *

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        print(f"Получено сообщение: {event.text}")
        return await handler(event, data)