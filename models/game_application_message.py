from datetime import datetime

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.game import Game


class GameApplicationMessage(Base):
    __tablename__ = "game_application_message"

    id: Mapped[int] = mapped_column(primary_key=True)

    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    game_id: Mapped[int] = mapped_column(ForeignKey("game.id", ondelete="CASCADE"))
    message_id: Mapped[int]
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    game: Mapped["Game"] = relationship()
