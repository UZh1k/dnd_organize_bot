from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from controllers.crud import CRUD
from models import Game


class GameController(CRUD):
    model = Game

    @classmethod
    def common_query(cls):
        return select(cls.model).options(joinedload(Game.city), selectinload(Game.tags))

    @classmethod
    async def get_unlinked_games(
        cls, user_id: int, session: AsyncSession
    ) -> Sequence[Game]:
        query = select(Game).where(
            Game.creator_id == user_id, Game.group_id.is_(None), Game.active.is_(True)
        )
        return (await session.execute(query)).scalars().all()

    @classmethod
    async def unlink_game_from_group(cls, group_id: int, session: AsyncSession):
        await session.execute(
            update(Game).where(Game.group_id == group_id).values(group_id=None)
        )

    @classmethod
    async def get_games_for_edit(
        cls, creator_id: int, session: AsyncSession
    ) -> Sequence[Game]:
        query = (
            select(Game)
            .where(Game.creator_id == creator_id)
            .where(Game.active.is_(True))
        )
        return (await session.execute(query)).scalars().all()
