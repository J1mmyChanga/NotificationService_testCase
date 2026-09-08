from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.common.core.database import AsyncSessionLocal
from app.common.user.repository.repository import UserRepository

router = Router()

@router.message(CommandStart())
async def cmd_start_handler(message: Message) -> None:
    telegram_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        repository = UserRepository(session=session)
        user = repository.get_by_telegram_id(telegram_id)
    if not user:
        repository.create(telegram_id=telegram_id)
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