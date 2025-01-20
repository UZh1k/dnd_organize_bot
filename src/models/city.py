from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
