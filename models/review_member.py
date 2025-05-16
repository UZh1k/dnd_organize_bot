from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from models import Base


class ReviewMember(Base):
    """
    The ones who can review game
    """
    __tablename__ = "review_member"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="CASCADE"), primary_key=True
    )
