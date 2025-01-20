from abc import ABC, abstractmethod
from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Base


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
        obj = await cls.get_one(value, session, field)
        if obj:
            return obj

        obj = cls.model(**({field: value} | other_values))
        session.add(obj)
        await session.flush()
        return obj

    @classmethod
    def common_query(cls):
        return select(cls.model)

    @classmethod
    async def get_one(
        cls, value: int | str, session: AsyncSession, field: str = "id"
    ) -> model:
        query = cls.common_query().where(value == getattr(cls.model, field))
        return (await session.execute(query)).scalars().first()

    @classmethod
    async def create(cls, model_dict: dict, session: AsyncSession):
        obj = cls.model(**model_dict)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj

    @classmethod
    async def get_list(cls, session: AsyncSession):
        return (
            (await session.execute(cls.common_query().order_by(cls.model.id)))
            .scalars()
            .all()
        )
