import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, func

from app.common.core.database import AsyncSessionLocal
from app.common.notification.models.notification import Notification, NotificationStatus
from app.common.channel.models.channel import ChannelStatus
from app.common.user.models.user import User
from app.common.channel.service.base import NotificationChannelRegistry
from app.common.core.metrics import NOTIFICATION_LAG, NOTIFICATIONS_TOTAL, EXTERNAL_API_REQUESTS, NOTIFICATIONS_PENDING, \
    WORKER_PROCESSING_TIME
from app.common.core.logger import logger
from app.common.notification.repository.repository import NotificationRepository
from app.common.user.repository.repository import UserRepository
from app.common.channel.repository.repository import ChannelRepository


async def process_pending_notifications(registry: NotificationChannelRegistry) -> None:
    # подсчет времени выполнения всей итерации воркера
    with WORKER_PROCESSING_TIME.time():
        async with AsyncSessionLocal() as session:
            now_utc = datetime.now(timezone.utc)

            repository = NotificationRepository(session=session)
            user_repository = UserRepository(session=session)
            channel_repository = ChannelRepository(session=session)
            # подсчет зависших уведомлений, чья очередь наступила

            pending_count = await repository.get_pending_notifications_count(now_utc)
            NOTIFICATIONS_PENDING.set(pending_count)
            notifications = await repository.get_pending_notifications_for_worker(now_utc)

            if not notifications:
                return

            for notification in notifications:
                await repository.change_status(notification, NotificationStatus.PROCESSING)

                # ИСПРАВЛЕНИЕ: Вычисляем lag до того, как использовать его в логах
                now_utc = datetime.now(timezone.utc)
                lag = (now_utc - notification.scheduled_time).total_seconds()

                log_context = {
                    "notification_id": str(notification.id),
                    "user_id": str(notification.user_id),
                    "channel": notification.channel,
                    "scheduled_time": notification.scheduled_time.isoformat(),
                    "lag_seconds": round(lag, 4),
                    "status": notification.status.value,
                    "service": "worker"
                }
                logger.info("Notification  updated to PROCESSING", extra=log_context)

                try:
                    delivery_channel = await channel_repository.get_by_user_id(notification.user_id, notification.channel)
                    channel = registry.get(notification.channel)

                    await channel.send(
                        channel_address=delivery_channel.address,
                        message_text=notification.message_text
                    )
                    await repository.change_status(notification, NotificationStatus.SENT)

                    # Записываем метрику задержки
                    NOTIFICATION_LAG.observe(max(0.0, lag))

                    # подсчет отправки уведомлений (успешных)
                    NOTIFICATIONS_TOTAL.labels(status="sent", channel=notification.channel).inc()
                    EXTERNAL_API_REQUESTS.labels(target=notification.channel, status_code="200").inc()
                    logger.info("Notification successfully sent and status updated to SENT", extra=log_context)

                except Exception as e:
                    logger.error(f"Failed to send notification {notification.id}: {e}")
                    notification.status = NotificationStatus.FAILED

                    # подсчет отправки уведомлений (ошибка)
                    status_code = getattr(e, "code", "500")
                    NOTIFICATIONS_TOTAL.labels(status="failed", channel=notification.channel).inc()
                    EXTERNAL_API_REQUESTS.labels(target=notification.channel, status_code=str(status_code)).inc()

                    logger.error(
                        f"Failed to process notification: {e}",
                        extra={**log_context, "error": str(e)},
                        exc_info=True
                    )

                await session.commit()


async def run_scheduler(registry: NotificationChannelRegistry, poll_interval: float = 1.0) -> None:
    while True:
        try:
            await process_pending_notifications(registry)
        except Exception as e:
            logger.error(f"Error in worker cycle: {e}")

        await asyncio.sleep(poll_interval)