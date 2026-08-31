import asyncio
import os
from app.channels.base import NotificationChannelRegistry
from app.channels.telegram import TelegramNotificationChannel
from app.worker.scheduler import run_scheduler
from app.config import settings

from app.core.metrics import start_metrics_server
from app.core.logger import logger


async def main():
    start_metrics_server(port=8002)
    logger.info("Worker service starting up", extra={"service": "worker"})

    registry = NotificationChannelRegistry()
    tg_channel = TelegramNotificationChannel(bot_token=settings.BOT_TOKEN)
    registry.register(tg_channel)

    try:
        logger.info("Scheduler started successfully", extra={"service": "worker"})
        await run_scheduler(registry, poll_interval=1.0)
    except Exception as e:
        logger.critical(
            f"Worker crashed with error: {e}",
            exc_info=True,
            extra={"service": "worker"}
        )
    finally:
        logger.info("Shutting down worker and closing connections...", extra={"service": "worker"})
        await tg_channel.close()


if __name__ == "__main__":
    asyncio.run(main())