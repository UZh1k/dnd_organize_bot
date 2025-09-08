from datetime import datetime
from enum import Enum, IntEnum

from sqlalchemy import BIGINT, SMALLINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.city import City
from models.game_tag import GameTag
from models.user import User


class GameFormat(IntEnum):
    text = 1
    online = 2
    offline = 3
    any = 4


class GameFormatText(Enum):
    text = "Текстовая"
    online = "Онлайн"
    offline = "Оффлайн"
    any = "Любой"


class GameType(IntEnum):
    company = 1
    one_shot = 2


class GameTypeText(Enum):
    company = "Кампания"
    one_shot = "Ваншот"


class Game(Base):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    group_id: Mapped[int | None] = mapped_column(BIGINT)
    post_id: Mapped[int | None] = mapped_column(BIGINT)

    format: Mapped[GameFormat] = mapped_column(SMALLINT)
    type: Mapped[GameType] = mapped_column(SMALLINT)
    system: Mapped[str]
    description: Mapped[str]
    min_players: Mapped[int] = mapped_column(SMALLINT)
    max_players: Mapped[int] = mapped_column(SMALLINT)
    free: Mapped[bool]
    min_age: Mapped[int] = mapped_column(SMALLINT)
    max_age: Mapped[int | None] = mapped_column(SMALLINT)
    time: Mapped[str]
    tech_requirements: Mapped[str]
    image: Mapped[str | None]
    city_id: Mapped[int | None] = mapped_column(
        ForeignKey("city.id", ondelete="CASCADE")
    )
    platform: Mapped[str | None]
    about_price: Mapped[str | None]
    redaction: Mapped[str | None]
    setting: Mapped[str | None]
    start_level: Mapped[str | None]

    active: Mapped[bool | None] = mapped_column(default=True)

    is_update: Mapped[bool] = mapped_column(default=False)
    last_update: Mapped[datetime | None]
    done: Mapped[bool | None]

    create_datetime: Mapped[datetime | None]
    first_post_datetime: Mapped[datetime | None]
    done_datetime: Mapped[datetime | None]

    city: Mapped["City"] = relationship()
    creator: Mapped["User"] = relationship()
    tags: Mapped[list[GameTag]] = relationship(GameTag, secondary="game_tag_link")
