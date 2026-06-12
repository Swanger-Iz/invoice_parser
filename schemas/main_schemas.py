from pydantic import BaseModel, Field


class ResponseFormat(BaseModel):
    constructor_name: str | None = Field(None, description="ФИО исполнителя", min_length=2)
    customer_name: str | None = Field(None, description="ФИО заказчика", min_length=2)
