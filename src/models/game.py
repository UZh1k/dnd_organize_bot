from datetime import datetime
from enum import IntEnum, Enum

from sqlalchemy import ForeignKey, SMALLINT, BIGINT
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.models.base import Base
from src.models.game_tag import GameTag


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
    about_price: Mapped[str | None]
    redaction: Mapped[str | None]
    setting: Mapped[str | None]
    start_level: Mapped[str | None]

    active: Mapped[bool | None] = mapped_column(default=True)

    last_update: Mapped[datetime | None]
    done: Mapped[bool | None]

    city: Mapped["City"] = relationship()
    tags: Mapped[list[GameTag]] = relationship(GameTag, secondary="game_tag_link")
