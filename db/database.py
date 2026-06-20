"""Определяются сущности для работы с БД"""

from config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Нужен для DDL операций имеет .run_sync()
async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True,  # Вывод всех запросов в консоль
    pool_size=5,  # Максимальное кол-во подключений
    max_overflow=10,  # Если макс. подключений уже не хватает
)

# Сессия - это обертка над движком и нужен для DML & DQL
async_session_factory = async_sessionmaker(async_engine)
