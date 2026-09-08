from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.channel.models.channel import ChannelStatus
from app.common.core.logger import logger
from app.common.notification.models.notification import Notification
from app.common.notification.repository.repository import NotificationRepository
from app.common.channel.repository.repository import ChannelRepository


async def create_notification(
    session: AsyncSession,
    channel_address: str,
    scheduled_time: datetime,
    message_text: str,
    channel: ChannelStatus
) -> Notification:
    
    repository = NotificationRepository(session=session)
    channel_repository = ChannelRepository(session=session)

    delivery_channel = await channel_repository.get_by_address(channel_address, channel)

    if not delivery_channel:
        raise ValueError(f"Delivery channel with channel address={channel_address} is not found")

    notification = await repository.create(
        user_id=delivery_channel.user_id,
        scheduled_time=scheduled_time,
        message_text=message_text,
        channel=channel
    )

    log_context = {
        "notification_id": str(notification.id),
        "user_id": str(delivery_channel.user_id),
        "channel": channel,
        "channel_address": channel_address,
        "scheduled_time": scheduled_time.isoformat(),
        "service": "api",
        "status": notification.status.value
    }

    logger.info("Notification successfully created in DB with status PENDING", extra=log_context)

    return notification