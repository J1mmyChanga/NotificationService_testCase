from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.user.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self) -> User:
        user = User()
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user