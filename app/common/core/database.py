from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.common.config import settings

# асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # логирование
    future=True,
)

# асинхронная сессия
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session