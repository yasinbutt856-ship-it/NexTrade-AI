import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from db.models import Base


def _get_async_database_url() -> str:
    raw = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./trading.db")
    if raw.startswith("postgres://") or raw.startswith("postgresql://"):
        return raw.replace("postgres://", "postgresql+asyncpg://", 1).replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
    return raw


DATABASE_URL = _get_async_database_url()

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255)"))
    except Exception:
        pass
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE users ADD COLUMN stripe_subscription_id VARCHAR(255)"))
    except Exception:
        pass
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE users ADD COLUMN usage_api_calls INTEGER DEFAULT 0"))
    except Exception:
        pass
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE users ADD COLUMN usage_bot_hours FLOAT DEFAULT 0.0"))
    except Exception:
        pass
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE users ADD COLUMN usage_trade_volume FLOAT DEFAULT 0.0"))
    except Exception:
        pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def close_db() -> None:
    await engine.dispose()
