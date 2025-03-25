from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import func, Index, BIGINT, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from models.base import Base


class ReviewReceiverTypeEnum(Enum):
    player = "player"
    dm = "dm"


class Review(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    receiver_type: Mapped[ReviewReceiverTypeEnum]

    value: Mapped[int]
    comment: Mapped[str | None]

    created: Mapped[datetime] = mapped_column(server_default=func.now())

    from_user: Mapped["User"] = relationship(
        primaryjoin="foreign(Review.from_user_id) == remote(User.id)"
    )
    to_user: Mapped["User"] = relationship(
        primaryjoin="foreign(Review.to_user_id) == remote(User.id)"
    )

    __table_args__ = (
        Index(None, "from_user_id", "to_user_id", "receiver_type", unique=True),
        Index(None, "to_user_id", "receiver_type"),
    )


@dataclass
class ReviewStatistic:
    total_count: int
    rating: float
    comments_count: int
