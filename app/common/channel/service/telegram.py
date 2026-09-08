from aiogram import Bot
from app.common.channels.service.base import BaseNotificationChannel
from aiogram.client.session.aiohttp import AiohttpSession
from app.common.config import settings


class TelegramNotificationChannel(BaseNotificationChannel):
    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token, session=AiohttpSession(proxy=settings.PROXY_URL))

    @property
    def channel_name(self) -> str:
        return "telegram"

    async def send(self, recipient_id: int, message_text: str) -> None:
        await self.bot.send_message(chat_id=recipient_id, text=message_text)

    async def close(self) -> None:
        await self.bot.session.close()