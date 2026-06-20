# from sqlalchemy import Column, Integer, MetaData, String, Table, LargeBinary
import datetime

from sqlalchemy import LargeBinary, MetaData, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

######## Declarative style - ORM ########


# Здесь хранятся метаданные для ORM
class Base(DeclarativeBase):
    pass


class UserRequestsORM(Base):
    __tablename__ = "user_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str]
    image_bytes: Mapped[bytes] = mapped_column(LargeBinary)
    constructor_name: Mapped[str]
    customer_name: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    # default - это на уровне приложения python
    # server_default - это на уровне СУБД


####### Imperative style i.e. - Core ########

# Здесь хранятся метаданные для Core
metadata_obj = MetaData()


# user_requests_table = Table(
#     "user_requests",
#     metadata_obj,
#     Column("id", Integer, primary_key=True, autoincrement=True),
#     Column("status", String),
#     Column("image_bytes", LargeBinary),
#     Column("constructor_name", String),
#     Column("customer_name", String),
# )
