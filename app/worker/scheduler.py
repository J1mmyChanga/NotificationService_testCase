import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Notification, NotificationStatus
from app.channels.base import NotificationChannelRegistry

logger = logging.getLogger(__name__)


async def process_pending_notifications(registry: NotificationChannelRegistry) -> None:
    """Один цикл обработки готовых к отправке уведомлений."""
    async with AsyncSessionLocal() as session:
        now_utc = datetime.now(timezone.utc)

        # 1. Выбираем уведомления, время которых наступило
        stmt = (
            select(Notification)
            .where(
                Notification.status == NotificationStatus.PENDING,
                Notification.scheduled_at <= now_utc
            )
            .limit(100)  # Пачками по 100 штук
            .with_for_update(skip_locked=True)  # Блокировка от гонки процессов
        )

        result = await session.execute(stmt)
        notifications = result.scalars().all()

        if not notifications:
            return

        for notification in notifications:
            # 2. Переводим статус в PROCESSING
            notification.status = NotificationStatus.PROCESSING
            await session.commit()

            try:
                # 3. Достаем нужный канал (например, 'telegram') и отправляем
                channel = registry.get(notification.channel)
                await channel.send(
                    recipient_id=notification.user_id,
                    message_text=notification.message_text
                )

                # 4. Успешно отправлено
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now(timezone.utc)
                logger.info(f"Notification {notification.id} sent successfully.")

            except Exception as e:
                # 5. Ошибка отправки (например, rate limit или блокировка бота)
                logger.error(f"Failed to send notification {notification.id}: {e}")
                notification.retry_count += 1
                notification.status = NotificationStatus.FAILED

            await session.commit()


async def run_scheduler(registry: NotificationChannelRegistry, poll_interval: float = 1.0) -> None:
    """Бесконечный цикл фонового воркера."""
    logger.info("🚀 Фоновый воркер отправки уведомлений запущен...")
    while True:
        try:
            await process_pending_notifications(registry)
        except Exception as e:
            logger.error(f"Ошибка в цикле воркера: {e}")

        await asyncio.sleep(poll_interval)