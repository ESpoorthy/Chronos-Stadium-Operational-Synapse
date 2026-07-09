"""
Async SQLAlchemy session factory and declarative base for Chronos Stadium AI.

All database configuration is derived from ``app.config.settings``.
Use ``get_db`` as a FastAPI dependency to obtain a scoped async session
that is automatically closed when the request ends.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config.settings import settings

engine = create_async_engine(settings.database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a scoped async database session.

    The session is automatically closed (and the connection returned to the
    pool) when the request context exits, regardless of whether an exception
    was raised.

    Yields:
        An open ``AsyncSession`` scoped to the current request.
    """
    async with AsyncSessionLocal() as session:
        yield session
