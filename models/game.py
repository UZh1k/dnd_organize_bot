from enum import IntEnum

from sqlalchemy import ForeignKey, SMALLINT, BIGINT
from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base

class GameFormat(IntEnum):
    text = 1
    online = 2
    offline = 3
    any = 4


class GameType(IntEnum):
    company = 1
    one_shot = 2


class Game(Base):
    __tablename__ = 'game'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    group_id: Mapped[int | None] = mapped_column(BIGINT)
    post_id: Mapped[int | None] = mapped_column(BIGINT)

    format: Mapped[GameFormat | None] = mapped_column(SMALLINT)
    type: Mapped[GameType | None] = mapped_column(SMALLINT)
    system: Mapped[str | None]
    description: Mapped[str | None]
    min_players: Mapped[int | None] = mapped_column(SMALLINT)
    max_players: Mapped[int | None] = mapped_column(SMALLINT)
    free: Mapped[bool | None]
    min_age: Mapped[int | None] = mapped_column(SMALLINT)
    max_age: Mapped[int | None] = mapped_column(SMALLINT)
    time: Mapped[str | None]
    tech_requirements: Mapped[str | None]
    other_requirements: Mapped[str | None]
    image: Mapped[str | None]
    city_id: Mapped[int | None] = mapped_column(ForeignKey('city.id'))

    active: Mapped[bool | None] = mapped_column(default=True)
