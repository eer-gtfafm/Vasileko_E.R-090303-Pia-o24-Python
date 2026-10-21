import time

from aiogram import BaseMiddleware
from aiogram.types import Message

import logging

logger = logging.getLogger("hotel_bot")


class LoggingMiddleware(BaseMiddleware):
    """Логирует каждое входящее сообщение пользователя и время обработки."""

    def __init__(self):
        self.messages_count = 0

    async def __call__(self, handler, event: Message, data: dict):
        self.messages_count += 1
        start = time.perf_counter()
        user = event.from_user
        name = user.full_name if user else "unknown"
        text = event.text or event.caption or f"[{event.content_type}]"
        logger.info("USER %s (%s): %s", user.id if user else "?", name, text)
        try:
            result = await handler(event, data)
        finally:
            duration = (time.perf_counter() - start) * 1000
            logger.info("Обработка заняла %.1f мс, всего сообщений: %d",
                        duration, self.messages_count)
        return result