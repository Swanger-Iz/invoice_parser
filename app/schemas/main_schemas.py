from typing import Literal

from database.models import UserRequestsORM
from logger import setup_logger
from pydantic import BaseModel, ConfigDict, Field

logger = setup_logger(__name__)


# For LLM response
class ModelResponseFormat(BaseModel):
    constructor_name: str | None = Field(None, description="ФИО исполнителя", min_length=2)
    customer_name: str | None = Field(None, description="ФИО заказчика", min_length=2)


# DTOs
class RequestsPostDTO(BaseModel):
    status: Literal["SUCCESS", "BAD"]
    image_bytes: bytes | None
    image_hash: str | None
    constructor_name: str | None = Field(None, description="ФИО исполнителя", min_length=2)
    customer_name: str | None = Field(None, description="ФИО заказчика", min_length=2)

    model_config = ConfigDict(from_attributes=True)

    def to_orm(self) -> "UserRequestsORM":
        """Конвертирует Pydantic-схему в ORM-модель."""

        return UserRequestsORM(
            status=self.status,
            image_bytes=self.image_bytes,
            image_hash=self.image_hash,
            constructor_name=self.constructor_name,
            customer_name=self.customer_name,
        )

    # from_orm() — это альтернативный конструктор.
    # На входе: принимает ORM-объект (UserRequestsORM)
    # На выходе: создает НОВЫЙ Pydantic-объект (ModelRequests)
    # Ключевой момент: from_orm() не трогает существующие данные.
    # Он просто читает поля из ORM-объекта и создает новый независимый объект Pydantic.
    @classmethod
    def from_orm(cls, orm_model: "UserRequestsORM") -> "RequestsPostDTO":
        """Создает Pydantic-схему из ORM-объекта."""
        return cls(
            id=orm_model.id,
            status=orm_model.status,
            image_bytes=orm_model.image_bytes,
            constructor_name=orm_model.constructor_name,
            customer_name=orm_model.customer_name,
        )


class RequestsAllDTO(RequestsPostDTO):
    id: int


class GetImageDTO(BaseModel):
    image_bytes: bytes


class GetImageHashDTO(BaseModel):
    image_hash: str

    constructor_name: str | None = Field(None, description="ФИО исполнителя", min_length=2)
    customer_name: str | None = Field(None, description="ФИО заказчика", min_length=2)


class RequestPreviewDTO(BaseModel):
    constructor_name: str | None = Field(None, description="ФИО исполнителя", min_length=2)
    customer_name: str | None = Field(None, description="ФИО заказчика", min_length=2)

    model_config = ConfigDict(from_attributes=True)
