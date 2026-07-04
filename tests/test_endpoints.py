from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app
from schemas.main_schemas import RequestPreviewDTO
from storage import task_storage


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

    @pytest.mark.skipif('config.getoption("--endpoint") != "tasks"')
    @pytest.mark.asyncio
    async def test_get_status_existing_task(self, async_client):
        with patch.dict(task_storage, {"task_id": "in_progress"}):
            response = await async_client.get("/status/task_id")

            assert response.status_code == 200
            assert response.json()["status"] == "in_progress"

    @pytest.mark.skipif('config.getoption("--endpoint") != "tasks"')
    @pytest.mark.asyncio
    async def test_get_status_not_found(self, async_client):
        response = await async_client.get("/status/1")
        assert response.status_code == 404

    @pytest.mark.skipif('config.getoption("--endpoint") != "requests"')
    @pytest.mark.asyncio
    async def test_get_all_requests_success(self, async_client):
        fake_data = [
            RequestPreviewDTO(id=1, constructor_name="Ilya Dyachenko", customer_name="Petr Pavlov"),
            RequestPreviewDTO(id=2, constructor_name="Dmitry Karamazov", customer_name="Ilya Karamazov"),
        ]
        with patch("api.v1.endpoints.requests.DQL_queries.get_all_request_data", AsyncMock(return_value=fake_data)):
            response = await async_client.get("/requests/")
            assert response.status_code == 200

    @pytest.mark.skipif('config.getoption("--endpoint") != "requests"')
    @pytest.mark.asyncio
    async def test_get_all_requests_error(self, async_client):
        with patch("api.v1.endpoints.requests.DQL_queries.get_all_request_data", AsyncMock(return_value=None)):
            response = await async_client.get("/requests/")
            assert response.status_code == 404
