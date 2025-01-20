from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class GameTagLink(Base):
    __tablename__ = "game_tag_link"

    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("game_tag.id", ondelete="CASCADE"), primary_key=True
    )

class GameTag(Base):
    __tablename__ = "game_tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]