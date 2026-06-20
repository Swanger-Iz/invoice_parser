from typing import Literal

from pydantic import BaseModel, Field

from db.db_tables import UserRequestsORM


class ResponseFormat(BaseModel):
    constructor_name: str | None = Field(None, description="ФИО исполнителя", min_length=2)
    customer_name: str | None = Field(None, description="ФИО заказчика", min_length=2)


# Caching
class ModelRequests(ResponseFormat):
    id: int = Field(default=0, description="request_id")
    status: Literal["SUCCESS", "BAD"]
    image_bytes: bytes

    def to_orm(self) -> "UserRequestsORM":
        """Конвертирует Pydantic-схему в ORM-модель."""

        return UserRequestsORM(status=self.status, image_bytes=self.image_bytes, constructor_name=self.constructor_name, customer_name=self.customer_name)

    # from_orm() — это альтернативный конструктор.
    # На входе: принимает ORM-объект (UserRequestsORM)
    # На выходе: создает НОВЫЙ Pydantic-объект (ModelRequests)
    # Ключевой момент: from_orm() не трогает существующие данные.
    # Он просто читает поля из ORM-объекта и создает новый независимый объект Pydantic.
    @classmethod
    def from_orm(cls, orm_model: "UserRequestsORM") -> "ModelRequests":
        """Создает Pydantic-схему из ORM-объекта."""
        return cls(
            id=orm_model.id,
            status=orm_model.status,
            image_bytes=orm_model.image_bytes,
            constructor_name=orm_model.constructor_name,
            customer_name=orm_model.customer_name,
        )
