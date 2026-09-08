from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.core.logger import logger
from app.common.notification.models.notification import Notification
from app.common.notification.repository.repository import NotificationRepository
from app.common.user.repository.repository import UserRepository


async def create_notification(
    session: AsyncSession,
    telegram_id: int,
    scheduled_time: datetime,
    message_text: str,
    channel: str
) -> Notification:
    
    repository = NotificationRepository(session=session)
    user_repository = UserRepository(session=session)

    user = await user_repository.get_by_telegram_id(session, telegram_id)

    if not user:
        raise ValueError(f"User with telegram_id={telegram_id} is not found")

    notification = await repository.create(
        session=session,
        user_id=user.id,
        scheduled_time=scheduled_time,
        message_text=message_text,
        channel=channel
    )

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