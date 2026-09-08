from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.notification.models.notification import Notification, NotificationStatus
from app.common.user.models.user import User


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_pending_notifications(self, )

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
            channel=channel
        )
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification