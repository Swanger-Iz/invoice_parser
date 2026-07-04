import pytest
import pytest_asyncio
from database.config import settings
from database.models import Base
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


def pytest_addoption(parser):
    parser.addoption("--endpoint", default="pages", choices=("pages", "requests", "get-fio"))


@pytest.fixture
def endpoint(request):
    return request.config.getoption("--endpoint")


#### SESSION FIXTURES
@pytest_asyncio.fixture
async def test_session():
    assert settings.MODE == "TEST"
    async_engine = create_async_engine(url=settings.DATABASE_URL_asyncpg)
    async_session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False, autoflush=False, autocommit=False)

    async with async_engine.begin() as conn:
        print("CREATING TABLES")
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        print("RETURNING SESSION")
        yield session

    async with async_engine.begin() as conn:
        print("DELETED ALL DATA")
        await conn.run_sync(Base.metadata.drop_all)
