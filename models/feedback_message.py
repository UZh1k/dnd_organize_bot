from datetime import datetime

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class FeedbackMessage(Base):
    __tablename__ = "feedback_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    message_id: Mapped[int]
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
