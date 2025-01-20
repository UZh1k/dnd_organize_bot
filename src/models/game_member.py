from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class GameMember(Base):
    __tablename__ = "game_member"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="CASCADE"), primary_key=True
    )
