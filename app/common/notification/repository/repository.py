from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.notification.models.notification import Notification, NotificationStatus


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_pending_notifications_count(self, curr_time) -> int:
        stmt = (
            select(func.count(Notification.id))
            .where(
                Notification.status == NotificationStatus.PENDING,
                Notification.scheduled_time <= curr_time
            )
        )
        pending_count = (await self.session.execute(stmt)).scalar() or 0
        return pending_count

    async def get_pending_notifications_for_worker(self, curr_time) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(
                Notification.status == NotificationStatus.PENDING,
                Notification.scheduled_time <= curr_time
            )
            .limit(100)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def change_status(self, notification, status) -> None:
        notification.status = status
        await self.session.commit()

    async def create(
        self,
        user_id: int,
        scheduled_time: datetime,
        message_text: str,
        channel: str
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            scheduled_time=scheduled_time,
            message_text=message_text,
            status=NotificationStatus.PENDING,
            channel=channel,
            retry_count=0
        )
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification