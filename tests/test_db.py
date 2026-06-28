import secrets
from contextlib import nullcontext

import pytest
import pytest_asyncio
from database.queries_core import DQL_queries
from database.queries_orm import DML_queries
from schemas.main_schemas import (
    RequestPreviewDTO,
    RequestsPostDTO,
)

### FIXTURES WITH VALUES
TEST_CASES = [
    {
        "rows": [],
        "exp": nullcontext(),
        "exp_count": 0,
    },
    {
        "rows": [
            RequestsPostDTO(
                status="BAD",
                image_bytes=b"10",
                image_hash="some34-first-12hash",
                constructor_name="Billy Harrington",
                customer_name="Van Dartkholm",
            ),
            RequestsPostDTO(
                status="SUCCESS",
                image_bytes=b"12",
                image_hash="some22-second-33hash",
                constructor_name="Harry Potter",
                customer_name="Hagrid Fatty",
            ),
            RequestsPostDTO(
                status="SUCCESS",
                image_bytes=b"123",
                image_hash="some33-third-282hash",
                constructor_name="Henry Morrison",
                customer_name="Shayla Willson",
            ),
        ],
        "exp": nullcontext(),
        "exp_count": 3,
        "ids": 2,
    },
    {
        "rows": [
            RequestsPostDTO(
                status="BAD",
                image_bytes=b"10",
                image_hash="some34-first-12hash",
                constructor_name="Billy Harrington",
                customer_name="Van Dartkholm",
            ),
            RequestsPostDTO(
                status="SUCCESS",
                image_bytes=b"12",
                image_hash="some22-second-33hash",
                constructor_name="Harry Potter",
                customer_name="Hagrid Fatty",
            ),
            RequestsPostDTO(
                status="SUCCESS",
                image_bytes=b"123",
                image_hash="some33-third-282has2222h",
                constructor_name="Henry Morrison",
                customer_name="Shayla Willson",
            ),
            RequestsPostDTO(
                status="BAD",
                image_bytes=b"121",
                image_hash="som1e22-second-33hash",
                constructor_name="Murad Arsenovich",
                customer_name="Alexey Karamazov",
            ),
            RequestsPostDTO(
                status="BAD",
                image_bytes=b"1223",
                image_hash="somess33-third-282hash",
                constructor_name="Mitya Karamazov",
                customer_name="Ilya Karamazov",
            ),
        ],
        "exp": nullcontext(),
        "exp_count": 5,
        "ids": 4,
    },
]


@pytest_asyncio.fixture(params=TEST_CASES)
async def session_with_data(test_session, request) -> dict:
    case_ = request.param
    rows = case_["rows"]

    for r in rows:
        await DML_queries.insert_new_data_to_user_requests(r, session=test_session)

    return {"session": test_session, "exp": case_["exp"], "exp_count": case_["exp_count"]}


#### DATABASE TESTING
class TestDatabase:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "rows, exp",
        [
            (
                [
                    RequestsPostDTO(
                        status="BAD",
                        image_bytes=b"10",
                        image_hash="some34-first-12hash",
                        constructor_name="Billy Harrington",
                        customer_name="Van Dartkholm",
                    ),
                    RequestsPostDTO(
                        status="SUCCESS",
                        image_bytes=b"12",
                        image_hash="some22-second-33hash",
                        constructor_name="Harry Potter",
                        customer_name="Hagrid Fatty",
                    ),
                ],
                nullcontext(),
            ),
            (
                [
                    RequestsPostDTO(
                        status="SUCCESS",
                        image_bytes=b"123",
                        image_hash="some33-third-282hash",
                        constructor_name="Henry Morrison",
                        customer_name="Shayla Willson",
                    )
                ],
                nullcontext(),
            ),
        ],
    )
    async def test_inserting(self, test_session, rows: list[RequestsPostDTO], exp):
        for r in rows:
            with exp:
                db_res = await DML_queries.insert_new_data_to_user_requests(r, session=test_session)
                assert db_res

    @pytest.mark.asyncio
    async def test_count_inserting(self, session_with_data: dict):
        """Test all 4 quieries"""
        session, exp, exp_count = session_with_data.values()

        validated_rows = await DQL_queries.get_all_request_data(session)

        if validated_rows is None:
            assert validated_rows is None
            return

        assert len(validated_rows) == exp_count

        print(f"\nvalidated_rows: {validated_rows}")
        print(f"exp_count: {exp_count}")

        for row in validated_rows:
            print(RequestPreviewDTO.model_validate(row))
            assert isinstance(row, RequestPreviewDTO)

    @pytest.mark.asyncio
    async def test_get_all_rows(self, session_with_data: dict):
        session, exp, exp_count = session_with_data.values()

        rows = await DQL_queries.get_all_request_data(session)
        if rows is None:
            assert rows is None
            return

        assert len(rows) == exp_count

    @pytest.mark.asyncio
    async def test_get_data_by_id(self, session_with_data: dict):
        session, exp, exp_count = session_with_data.values()
        if exp_count == 0:
            return

        for i in range(3):
            random_id = secrets.choice(range(exp_count - 1))
            res = await DQL_queries.get_preview_request_data_by_id(session, random_id)
            if res is None:
                continue
            assert random_id == res.id
