from enum import Enum

from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base


class ReviewReceiverTypeEnum(Enum):
    player = "player"
    dm = "dm"

class Review(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_user_id: Mapped[int]
    to_user_id: Mapped[int] = mapped_column(index=True)
    receiver_type: Mapped[ReviewReceiverTypeEnum]

    value: Mapped[int]
    comment: Mapped[str | None]
