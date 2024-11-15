from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class GameMember(Base):
    __tablename__ = 'game_member'
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey('game.id'), primary_key=True)
