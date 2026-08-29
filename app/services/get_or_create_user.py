from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User


async def create_user(session: AsyncSession, telegram_id: int) -> tuple[User, bool]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return user, False

    new_user = User(telegram_id=telegram_id)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user, True