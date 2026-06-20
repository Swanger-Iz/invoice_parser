"""Здесь храняться все функции для взаимодействия с БД"""

import sys
from pathlib import Path

sys.path.insert(1, str(Path(__file__).parent.parent))

from database import async_engine, async_session_factory

from db.db_tables import Base, metadata_obj
from schemas.main_schemas import ModelRequests

response_list = [
    ModelRequests(id=1, status="SUCCESS", constructor_name="Кучков Игорь Маркович", customer_name="Валеев Артур Хамзадович", image_bytes=bytes(10)),
    ModelRequests(id=2, status="SUCCESS", constructor_name="Горемыкин Артем Динисович", customer_name="Уразбахтин Тимур Фанильевич", image_bytes=bytes(12)),
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
    async def insert_new_data_to__user_requests(requests: list[ModelRequests]):
        rows = [req.to_orm() for req in requests]
        try:
            async with async_session_factory() as session:
                # session.add()
                session.add_all(rows)
                await session.commit()

                print(f"✅ Вставлено {len(rows)} записей")
                return True
        except Exception as e:
            print(f"❌ Ошибка вставки: {e}")
            return None


###### TESTS #######
# import asyncio
# from queries import get_all_request_data, get_basic_request_data_by_id
# async def main():
#     await DDL_queries.truncate_tables()


# print("Launching: create_table__user_requests")
# await create_table__user_requests()

# print("Launching: insert_data_to__user_requests")
# await insert_data_to__user_requests(response_list)
# await get_basic_request_data_by_id(2)
# await get_all_request_data()
# ...


# if __name__ == "__main__":
#     asyncio.run(main())
