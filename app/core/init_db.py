import asyncio
import logging
import sys
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.models import Base, User, Notification

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def init_models() -> None:
    logger.info("Connecting to PostgreSQL...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Tables successfully created!")
    except Exception as e:
        logger.error(f"❌ Error while initializing database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_models())