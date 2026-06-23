# from sqlalchemy import Column, Integer, MetaData, String, Table, LargeBinary
import datetime

from logger import setup_logger
from sqlalchemy import LargeBinary, MetaData, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = setup_logger(__name__)


######## Declarative style - ORM ########


# Здесь хранятся метаданные для ORM
class Base(DeclarativeBase):
    pass


class UserRequestsORM(Base):
    __tablename__ = "user_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str]
    image_bytes: Mapped[bytes] = mapped_column(LargeBinary)
    image_hash: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    constructor_name: Mapped[str] = mapped_column(nullable=True)
    customer_name: Mapped[str] = mapped_column(nullable=True)
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
