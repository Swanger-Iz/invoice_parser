from database.dependencies import SessionDep
from database.models import UserRequestsORM
from schemas.main_schemas import GetImageDTO, RequestPreviewDTO
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
    async def get_all_request_data(session: SessionDep) -> list[RequestPreviewDTO] | None:
        """Получить: constructor_name, customer_name, image_bytes
            для всех записей.

        Returns:
            list: [constructor_name, customer_name, image_bytes]
        """
        try:
            query = select(UserRequestsORM.constructor_name, UserRequestsORM.customer_name)
            res = await session.execute(query)
            rows = res.all()
            validated_rows = [RequestPreviewDTO.model_validate(row, from_attributes=True) for row in rows]
            print(validated_rows)
            return validated_rows
        except Exception as e:
            print(f"Error: {e}")
            raise

    @staticmethod
    async def get_preview_request_data_by_id(session: SessionDep, request_id: int) -> RequestPreviewDTO:
        """Получить: constructor_name, customer_name, image_bytes
            для опдереденного request_id.

        Returns:
            (constructor_name, customer_name, image_bytes)
        """
        ### получим один объект
        # customer = session.get(UserRequestsORM, request_id)
        try:
            ### Получаем неск объектов
            query = (
                select(UserRequestsORM.constructor_name, UserRequestsORM.customer_name)
                # .select_from(UserRequestsORM)
                .filter(UserRequestsORM.id == request_id)
            )  # .compile(compile_kwargs={"literal_binds": True})
            result = await session.execute(query)

            row = result.one_or_none()

            if row is None:
                return None
            validated_row = RequestPreviewDTO.model_validate(row, from_attributes=True)
            print("RESPONSE:", validated_row)
            return validated_row
        except Exception as e:
            print(f"Error: {e}")
            raise

    @staticmethod
    async def get_image_by_id(session: SessionDep, request_id: int) -> GetImageDTO:
        query = select(UserRequestsORM.image_bytes).where(UserRequestsORM.id == request_id)
        result = await session.execute(query)

        row: bytes = result.one_or_none()
        if row is None:
            return None
        return GetImageDTO.model_validate(row, from_attributes=True)
