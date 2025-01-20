from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.crud import CRUD
from src.models import GameApplication


class GameApplicationController(CRUD):
    model = GameApplication

    @classmethod
    async def create(cls, game_id: int, user_id: int, session: AsyncSession):
        session.add(GameApplication(game_id=game_id, user_id=user_id))
        await session.flush()

    @classmethod
    async def get_one(cls, game_id: int, user_id: int, session: AsyncSession):
        query = select(GameApplication).where(
            GameApplication.game_id == game_id, GameApplication.user_id == user_id
        )
        return (await session.execute(query)).scalars().first()

    @classmethod
    async def set_status(
        cls, game_id: int, user_id: int, accepted: bool, session: AsyncSession
    ):
        await session.execute(
            update(GameApplication)
            .where(
                GameApplication.game_id == game_id, GameApplication.user_id == user_id
            )
            .values(accepted=accepted)
        )
