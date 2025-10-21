from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from controllers.crud import CRUD
from models import GameApplicationMessage


class GameApplicationMessageController(CRUD):
    model = GameApplicationMessage

    @classmethod
    async def get_one_for_answer(
        cls, receiver_id: int, message_id: int, session: AsyncSession
    ):
        query = (
            select(GameApplicationMessage)
            .where(
                GameApplicationMessage.receiver_id == receiver_id,
                GameApplicationMessage.message_id == message_id,
            )
            .options(joinedload(GameApplicationMessage.game))
        )
        return (await session.execute(query)).scalars().first()
