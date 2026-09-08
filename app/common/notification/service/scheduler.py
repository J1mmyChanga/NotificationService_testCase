import asyncio
from datetime import datetime, timezone, timedelta

from app.common.core.database import AsyncSessionLocal
from app.common.notification.models.notification import NotificationStatus
from app.common.channel.service.base import NotificationChannelRegistry
from app.common.core.metrics import NOTIFICATION_LAG, NOTIFICATIONS_TOTAL, EXTERNAL_API_REQUESTS, NOTIFICATIONS_PENDING, \
    WORKER_PROCESSING_TIME
from app.common.core.logger import logger
from app.common.notification.repository.repository import NotificationRepository
from app.common.channel.repository.repository import ChannelRepository

MAX_RETRIES = 3
BASE_RETRY_DELAY_SECONDS = 5.0

async def process_pending_notifications(registry: NotificationChannelRegistry) -> None:
    # подсчет времени выполнения всей итерации воркера
    with WORKER_PROCESSING_TIME.time():
        async with AsyncSessionLocal() as session:
            now_utc = datetime.now(timezone.utc)

            repository = NotificationRepository(session=session)
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

                current_retry_count = getattr(notification, "retry_count", 0)

                log_context = {
                    "notification_id": str(notification.id),
                    "user_id": str(notification.user_id),
                    "channel": notification.channel,
                    "scheduled_time": notification.scheduled_time.isoformat(),
                    "lag_seconds": round(lag, 4),
                    "status": notification.status.value,
                    "retry_count": current_retry_count,
                    "service": "worker"
                }
                logger.info("Notification  updated to PROCESSING", extra=log_context)

                try:
                    delivery_channel = await channel_repository.get_by_user_id(notification.user_id,
                                                                               notification.channel)
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
                    status_code = getattr(e, "code", getattr(e, "status_code", "500"))
                    EXTERNAL_API_REQUESTS.labels(target=notification.channel, status_code=str(status_code)).inc()
                    # Проверяем возможность повторной попытки
                    if current_retry_count < MAX_RETRIES:
                        new_retry_count = current_retry_count + 1
                        # Если есть retry_after (например, при HTTP 429), используем его, иначе Exponential Backoff
                        retry_after = getattr(e, "retry_after", None)
                        if retry_after is not None:
                            try:
                                delay_seconds = float(retry_after)
                            except (ValueError, TypeError):
                                delay_seconds = BASE_RETRY_DELAY_SECONDS * (2 ** current_retry_count)
                        else:
                            delay_seconds = BASE_RETRY_DELAY_SECONDS * (2 ** current_retry_count)
                        # Переносим время следующей отправки и возвращаем статус PENDING
                        notification.retry_count = new_retry_count
                        notification.scheduled_time = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
                        await repository.change_status(notification, NotificationStatus.PENDING)
                        NOTIFICATIONS_TOTAL.labels(status="retrying", channel=notification.channel).inc()
                        logger.warning(
                            f"Transient error sending notification {notification.id}. "
                            f"Scheduling retry {new_retry_count}/{MAX_RETRIES} in {delay_seconds}s. Error: {e}",
                            extra={
                                **log_context,
                                "next_retry_count": new_retry_count,
                                "delay_seconds": delay_seconds,
                                "error": str(e)
                            }
                        )
                    else:
                        await repository.change_status(notification, NotificationStatus.FAILED)
                        NOTIFICATIONS_TOTAL.labels(status="failed", channel=notification.channel).inc()
                        logger.error(
                            f"Failed to process notification after {MAX_RETRIES} retries: {e}",
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
