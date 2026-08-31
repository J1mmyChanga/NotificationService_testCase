from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models import Notification, NotificationStatus, User


async def create_notification(session: AsyncSession, telegram_id: int, scheduled_time: datetime,
                              message_text: str, channel: str) -> Notification:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError(f"User with telegram_id={telegram_id} is not found")

    notification = Notification(
        user_id=user.id,
        scheduled_time=scheduled_time,
        message_text=message_text,
        status=NotificationStatus.PENDING,
        channel=channel
    )
    session.add(notification)
    await session.commit()
    await session.refresh(notification)

    log_context = {
        "notification_id": str(notification.id),
        "user_id": str(telegram_id),
        "channel": channel,
        "scheduled_time": scheduled_time.isoformat(),
        "service": "api",
        "status": notification.status.value
    }

    logger.info("Notification successfully created in DB with status PENDING", extra=log_context)

    return notification