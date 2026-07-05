import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from api.v1.endpoints.get_fio import launch_model
from httpx import ASGITransport, AsyncClient
from main import app
from schemas.main_schemas import GetImageDTO, RequestPreviewDTO
from storage import task_storage


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client


class TestEndpoints:

    ## Pages ----------------------------------------------------------------
    @pytest.mark.pages
    @pytest.mark.asyncio
    async def test_get(self, async_client):
        response = await async_client.get("/")
        assert response.status_code == 200

    @pytest.mark.pages
    @pytest.mark.asyncio
    async def test_get_status_existing_task(self, async_client):
        with patch.dict(task_storage, {"task_id": "in_progress"}):
            response = await async_client.get("/status/task_id")

            assert response.status_code == 200
            assert response.json()["status"] == "in_progress"

    @pytest.mark.pages
    @pytest.mark.asyncio
    async def test_get_status_not_found(self, async_client):
        response = await async_client.get("/status/1")
        assert response.status_code == 404

    ## Requests ----------------------------------------------------------------
    @pytest.mark.requests
    @pytest.mark.asyncio
    async def test_get_all_requests_success(self, async_client):
        fake_data = [
            RequestPreviewDTO(id=1, constructor_name="Ilya Dyachenko", customer_name="Petr Pavlov"),
            RequestPreviewDTO(id=2, constructor_name="Dmitry Karamazov", customer_name="Ilya Karamazov"),
        ]
        with patch("api.v1.endpoints.requests.DQL_queries.get_all_request_data", AsyncMock(return_value=fake_data)):
            response = await async_client.get("/requests/")
            assert response.status_code == 200

    @pytest.mark.requests
    @pytest.mark.asyncio
    async def test_get_all_requests_error(self, async_client):
        with patch("api.v1.endpoints.requests.DQL_queries.get_all_request_data", AsyncMock(return_value=None)):
            response = await async_client.get("/requests/")
            assert response.status_code == 404

    @pytest.mark.requests
    @pytest.mark.asyncio
    async def test_get_row_by_id_success(self, async_client):
        fake_data = RequestPreviewDTO(id=2, constructor_name="Dmitry Karamazov", customer_name="Ilya Karamazov")
        with patch("api.v1.endpoints.requests.DQL_queries.get_preview_request_data_by_id", AsyncMock(return_value=fake_data)):
            response = await async_client.get("/requests/2")
            assert response.status_code == 200

    @pytest.mark.requests
    @pytest.mark.asyncio
    async def test_get_row_by_id_error_id_is_string(self, async_client):
        response = await async_client.get("/requests/wrong_id")
        assert response.status_code == 403

    @pytest.mark.requests
    @pytest.mark.asyncio
    async def test_get_row_by_id_error_id_is_negative(self, async_client):
        response = await async_client.get("/requests/-1")
        assert response.status_code == 404

    @pytest.mark.requests
    @pytest.mark.asyncio
    async def test_get_row_by_id_error_id_is_not_found_in_db(self, async_client):
        with patch("api.v1.endpoints.requests.DQL_queries.get_preview_request_data_by_id", AsyncMock(return_value=None)):
            response = await async_client.get("/requests/-1")
            assert response.status_code == 404

    @pytest.mark.requests
    @pytest.mark.asyncio
    async def test_get_image_bytes_by_id(self, async_client):
        fake_image = GetImageDTO(image_bytes=b"10")
        with patch("api.v1.endpoints.requests.DQL_queries.get_image_by_id", AsyncMock(return_value=fake_image)):
            response = await async_client.get("/requests/1/image")
            assert response.status_code == 200

    @pytest.mark.requests
    @pytest.mark.asyncio
    async def test_get_image_bytes_by_id_error_id_is_string(self, async_client):
        response = await async_client.get("/requests/wrong_id/image")
        assert response.status_code == 403

    @pytest.mark.requests
    @pytest.mark.asyncio
    async def test_get_image_bytes_by_id_error_id_is_negative(self, async_client):
        response = await async_client.get("/requests/-1/image")
        assert response.status_code == 404

    ## Get-fio ----------------------------------------------------------------
    @pytest.mark.get_fio
    @pytest.mark.asyncio
    async def test_get_fio_success(self, async_client):
        with patch("api.v1.endpoints.get_fio.DQL_queries.get_image_by_hash", AsyncMock(return_value=None)):
            with patch("api.v1.endpoints.get_fio.launch_model", AsyncMock(return_value=None)):
                response = await async_client.post("/api/v1/get_fio", files={"upload_file": ("test.jpg", b"10", "image/jpeg")})
                assert response.status_code == 202
                assert response.json()["status"] == "in_process"
                assert "task_id" in response.json()

    @pytest.mark.get_fio
    @pytest.mark.parametrize(
        "name, bytes, status_code",
        [("test.jpg", b"0" * (21 * 1024 * 1024), 415), ("test.mp4", b"10", 415)],
    )
    @pytest.mark.asyncio
    async def test_get_fio_errors(self, async_client, name, bytes, status_code):
        # TESTING: image has wrong format
        # TESTING: image has too big size
        response = await async_client.post("/api/v1/get_fio", files={"upload_file": (name, bytes, "image/jpeg")})
        assert response.status_code == status_code

    ### Get-fio - Background Task ----------------------------------------------------------------
    @pytest.mark.get_fio_bt
    @pytest.mark.asyncio
    async def test_bt_launch_model_success(self):
        fake_response = {"structured_response": MagicMock(id=1, constructor_name="Ivan Karamazov", customer_name="Mitya Karamazov")}
        task_id = "test-task-id"

        with patch("api.v1.endpoints.get_fio.extractor_agent.safely_exec_agent", AsyncMock(return_value=fake_response)):
            with patch("api.v1.endpoints.get_fio.DML_queries.insert_new_data_to_user_requests", AsyncMock(return_value=None)):
                await launch_model(image_in_bytes=b"fake_bytes", session=MagicMock(), task_id=task_id)

        assert task_storage[task_id] == "success"

    @pytest.mark.get_fio_bt
    @pytest.mark.asyncio
    async def test_bt_launch_model_errors(self):
        task_id_timeout = "test-task-id-timeout"
        task_id_none = "test-task-id-none"

        with patch("api.v1.endpoints.get_fio.extractor_agent.safely_exec_agent", AsyncMock(side_effect=asyncio.TimeoutError)):
            await launch_model(image_in_bytes=b"fake_bytes", session=MagicMock(), task_id=task_id_timeout)

        assert task_storage[task_id_timeout] == "error"

        with patch("api.v1.endpoints.get_fio.extractor_agent.safely_exec_agent", AsyncMock(return_value=None)):
            await launch_model(image_in_bytes=b"fake_bytes", session=MagicMock(), task_id=task_id_none)

        assert task_storage[task_id_none] == "error"
