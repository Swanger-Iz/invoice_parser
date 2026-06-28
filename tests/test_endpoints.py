from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app
from storage import task_storage


def pytest_addoption(parser):
    parser.addoption("--endpoint", default="pages", choises=("pages", "requests", "get-fio"))


@pytest.fixture
def endpoint(request):
    return request.config.getoption("--endpoint")


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client


class TestEndpoints:

    @pytest.mark.skipif('config.getoption("--endpoint") != "pages"')
    @pytest.mark.asyncio
    async def test_get(self, async_client):
        response = await async_client.get("/")
        assert response.status_code == 200

    @pytest.mark.skipif('config.getoption("--endpoint") != "pages"')
    @pytest.mark.asyncio
    async def test_get_status_existing_task(self, async_client):
        with patch.dict(task_storage, {"task_id": "in_progress"}):
            response = await async_client.get("/status/task_id")

            assert response.status_code == 200
            assert response.json()["status"] == "in_progress"

    @pytest.mark.skipif('config.getoption("--endpoint") != "pages"')
    @pytest.mark.asyncio
    async def test_get_status_not_found(self, async_client):
        response = await async_client.get("/status/1")
        assert response.status_code == 404

    @pytest.mark.skipif('config.getoption("--endpoint") != "requests"')
    @pytest.mark.asyncio
    async def test_get_all_requests(self): ...
