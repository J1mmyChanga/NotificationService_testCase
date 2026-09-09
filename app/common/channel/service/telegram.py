from aiogram import Bot
from app.common.channel.service.base import BaseNotificationChannel
from aiogram.client.session.aiohttp import AiohttpSession
from app.common.config import settings
from app.common.channel.models.channel import ChannelStatus


class TelegramNotificationChannel(BaseNotificationChannel):
    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token, session=AiohttpSession(proxy=settings.PROXY_URL))

    @property
    def channel_name(self) -> str:
        return ChannelStatus.TELEGRAM

    async def send(self, channel_address: str, message_text: str) -> None:
        await self.bot.send_message(chat_id=int(channel_address), text=message_text)

    async def close(self) -> None:
        await self.bot.session.close()