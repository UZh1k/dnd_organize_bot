from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.crud import CRUD
from models import GameMember


class GameMemberController(CRUD):
    model = GameMember

    @classmethod
    async def delete_game_member(
        cls, game_id: int, user_id: int, session: AsyncSession
    ):
        await session.execute(
            delete(GameMember).where(
                GameMember.game_id == game_id, GameMember.user_id == user_id
            )
        )

    @classmethod
    async def count_game_members(cls, game_id: int, session: AsyncSession) -> int:
        query = select(func.count(GameMember.user_id)).where(
            GameMember.game_id == game_id
        )
        return await session.scalar(query)
