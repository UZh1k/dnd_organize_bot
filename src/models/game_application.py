from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class GameApplication(Base):
    __tablename__ = "game_application"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="CASCADE"), primary_key=True
    )
    accepted: Mapped[bool | None]
