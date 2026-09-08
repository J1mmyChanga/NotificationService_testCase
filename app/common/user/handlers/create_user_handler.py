from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.common.channel.models.channel import ChannelStatus
from app.common.core.database import AsyncSessionLocal
from app.common.user.repository.repository import UserRepository
from app.common.channel.repository.repository import ChannelRepository

router = Router()

@router.message(CommandStart())
async def cmd_start_handler(message: Message) -> None:
    telegram_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        repository = ChannelRepository(session=session)
        user_repository = UserRepository(session=session)
        delivery_channel = await repository.get_channel_by_address(str(telegram_id), ChannelStatus.TELEGRAM)
    if not delivery_channel:
        user = await user_repository.create()
        new_delivery_channel = await repository.create_delivery_address(user.id, ChannelStatus.TELEGRAM, str(telegram_id))
        await message.answer(
            f"Привет, {message.from_user.first_name}!\n"
            f"Вы успешно зарегистрированы в системе отложенных напоминаний.\n"
            f"Ваш ID: {telegram_id}\n"
        )
    else:
        await message.answer(
            f"С возвращением, {message.from_user.first_name}!\n"
            f"Вы уже подписаны на получение уведомлений.\n"
            f"Ваш ID: {telegram_id}\n"
        )