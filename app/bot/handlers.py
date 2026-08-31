from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.database import AsyncSessionLocal
from app.services.get_or_create_user import get_or_create_user

router = Router()

@router.message(CommandStart())
async def cmd_start_handler(message: Message) -> None:
    telegram_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        user, created = await get_or_create_user(session, telegram_id)

    if created:
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