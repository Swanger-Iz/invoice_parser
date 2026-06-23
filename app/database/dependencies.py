"""Определяются сущности для работы с БД"""

from typing import Annotated

from database.config import settings
from fastapi import Depends
from logger import setup_logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = setup_logger(__name__)


# Нужен для DDL операций имеет .run_sync()
async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True,  # Вывод всех запросов в консоль
    pool_size=5,  # Максимальное кол-во подключений
    max_overflow=10,  # Если макс. подключений уже не хватает
)

# Сессия - это обертка над движком и нужен для DML & DQL
async_session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False, autoflush=False, autocommit=False)


async def get_session():
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
            # logger.info(f"Error: {e}")


# Depency Injection
SessionDep = Annotated[AsyncSession, Depends(get_session)]
