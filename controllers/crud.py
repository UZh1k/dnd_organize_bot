from abc import ABC, abstractmethod
from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base


class CRUD(ABC):

    @property
    @abstractmethod
    def model(self) -> Type[Base]:
        pass

    @classmethod
    async def get_or_create(
        cls,
        value: int | str,
        field: str,
        session: AsyncSession,
        other_values: dict | None = None,
    ) -> model:
        other_values = other_values or {}
        query = select(cls.model).where(value == getattr(cls.model, field))
        obj = (await session.execute(query)).scalars().first()
        if obj:
            return obj

        obj = cls.model(**({field: value} | other_values))
        session.add(obj)
        await session.flush()
        return obj

    @classmethod
    async def get_one(
        cls, value: int | str, session: AsyncSession, field: str = "id"
    ) -> model:
        query = select(cls.model).where(value == getattr(cls.model, field))
        return (await session.execute(query)).scalars().first()
