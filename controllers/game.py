from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from controllers.crud import CRUD
from models import Game


class GameController(CRUD):
    model = Game

    @classmethod
    def common_query(cls):
        return select(cls.model).options(joinedload(Game.city))

    @classmethod
    async def get_unlinked_games(
        cls, user_id: int, session: AsyncSession
    ) -> list[Game]:
        query = select(Game).where(Game.creator_id == user_id, Game.group_id.is_(None))
        return (await session.execute(query)).scalars().all()

    @classmethod
    async def unlink_game_from_group(cls, group_id: int, session: AsyncSession):
        await session.execute(
            update(Game).where(Game.group_id == group_id).values(group_id=None)
        )