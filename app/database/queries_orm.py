"""Здесь храняться все функции для взаимодействия с БД"""

import sys
from pathlib import Path

sys.path.insert(1, str(Path(__file__).parent.parent))

from custom_errors import InsertingIntoDBError
from database.dependencies import SessionDep, async_engine
from database.models import Base, metadata_obj
from logger import setup_logger
from schemas.main_schemas import RequestsPostDTO

logger = setup_logger(__name__)

response_list = [
    RequestsPostDTO(
        # id=1,
        status="BAD",
        image_bytes=bytes(10),
        image_hash="1234g3d12dwe1dd",
        constructor_name="Кучков Игорь Маркович",
        customer_name="Валеев Артур Хамзадович",
    ),
    RequestsPostDTO(
        # id=2,
        status="SUCCESS",
        image_bytes=bytes(12),
        image_hash="fdasfdasfdas",
        constructor_name="Горемыкин Артем Динисович",
        customer_name="Уразбахтин Тимур Фанильевич",
    ),
]


#### DDL ####
class DDL_queries:
    @staticmethod
    async def create_table_user_requests():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def truncate_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


#### DML ####
class DML_queries:
    @staticmethod
    async def insert_new_data_to_user_requests(row: RequestsPostDTO, session: SessionDep) -> bool:
        try:
            row = row.to_orm()
            session.add(row)
            # session.add_all(rows)
            await session.commit()

            logger.info(f"GOOD: Вставлена строка: {row}")
            return True
        except Exception as e:
            logger.info(f"BAD: Ошибка вставки: {e}")
            raise InsertingIntoDBError


###### TESTS #######


# from queries import get_all_request_data, get_basic_request_data_by_id


# await DML_queries.insert_new_data_to_user_requests(response_list)
# await DQL_queries.get_all_request_data()
# await DQL_queries.get_preview_request_data_by_id(2)


# logger.info("Launching: create_table__user_requests")
# await create_table__user_requests()

# logger.info("Launching: insert_data_to__user_requests")
# await insert_data_to__user_requests(response_list)
# await get_basic_request_data_by_id(2)
# await get_all_request_data()
# ...
