from database import async_engine, async_session_factory
from db_tables import UserRequestsORM
from sqlalchemy import select

### Нельзя использовать f строки, чтобы защититься от SQL инъекций
# Пример 1.
# stmt = text(
#         "UPDATE workers SET username=:username WHERE id=:id"
#     ).bindparams(username=new_username, id=worker_id)
# conn.execute(stmt)
# conn.commit()

# Пример 2
# stmt = (
#     update(workers_table)
#     .values(username=new_username)
#     # .where(workers_table.c.id==worker_id)
#     .filter_by(id=worker_id)
# )
# conn.execute(stmt)
# conn.commit()


# async def update_customer_name__from_user_requests_imp(id: int):
#     async with async_engine.connect() as conn:
#         query = select(
#             UserRequestsORM.id,
#             UserRequestsORM.constructor_name,
#         ).where()
#         # res = session.exe


class DQL_queries:
    @staticmethod
    async def get_basic_request_data_by_id(inp_customer_id: int):
        """Получить: constructor_name, customer_name, image_bytes
            для опдереденного inp_customer_id.

        Returns:
            (constructor_name, customer_name, image_bytes)
        """
        async with async_session_factory() as session:
            ### получим один объект
            # customer = session.get(UserRequestsORM, inp_customer_id)
            try:
                ### Получаем неск объектов
                query = (
                    select(UserRequestsORM.constructor_name, UserRequestsORM.customer_name, UserRequestsORM.image_bytes)
                    # .select_from(UserRequestsORM)
                    .filter(UserRequestsORM.id == inp_customer_id)
                )  # .compile(compile_kwargs={"literal_binds": True})
                result = await session.execute(query)

                row = result.one_or_none()

                if row is None:
                    return None
                return (row.constructor_name, row.customer_name, row.image_bytes)
            except Exception as e:
                print(f"Error: {e}")
                return None

    @staticmethod
    async def get_all_request_data():
        """Получить: constructor_name, customer_name, image_bytes
            для всех записей.

        Returns:
            list: [constructor_name, customer_name, image_bytes]
        """
        async with async_session_factory() as session:
            try:
                query = select(UserRequestsORM.constructor_name, UserRequestsORM.customer_name, UserRequestsORM.image_bytes)
                res = await session.execute(query)
                rows = res.all()

                return rows
            except Exception as e:
                print(f"Error: {e}")
                return None
