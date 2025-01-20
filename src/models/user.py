from datetime import datetime
from enum import IntEnum, Enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, SMALLINT, BIGINT

from src.models.base import Base


class UserType(IntEnum):
    admin = 0
    dm = 1
    player = 2
    both = 3


class UserTypeText(Enum):
    admin = "Админ"
    dm = "Мастер игры"
    player = "Игрок"
    both = "Игрок и мастер игры"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    username: Mapped[str | None]

    name: Mapped[str | None]
    age: Mapped[int | None]
    city_id: Mapped[int | None] = mapped_column(
        ForeignKey("city.id", ondelete="CASCADE")
    )
    timezone: Mapped[str | None]

    user_type: Mapped[UserType | None] = mapped_column(SMALLINT)
    bio: Mapped[str | None]
    registered: Mapped[bool] = mapped_column(default=False)
    banned: Mapped[bool] = mapped_column(default=False)
    commands_count: Mapped[int] = mapped_column(default=0)
    last_update: Mapped[datetime | None]

    city: Mapped["City"] = relationship()
