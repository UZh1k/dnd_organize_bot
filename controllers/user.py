from operator import or_
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from controllers.crud import CRUD
from models import GameMember, Game, Review, ReviewReceiverTypeEnum
from models.user import User


class UserController(CRUD):
    model = User

    @classmethod
    def common_query(cls):
        return select(cls.model).options(joinedload(User.city))

    @classmethod
    async def get_by_id_or_username(
        cls, identifier: str, session: AsyncSession
    ) -> User | None:
        if identifier.isdigit():
            return await cls.get_one(int(identifier), session)
        else:
            return await cls.get_one(identifier, session, "username")

    @classmethod
    async def get_players_to_review(
        cls, user_id: int, session: AsyncSession
    ) -> Sequence[User]:
        query = (
            select(User)
            .join(GameMember, User.id == GameMember.user_id)
            .join(Game, Game.id == GameMember.game_id)
            .where(
                or_(
                    Game.creator_id == user_id,
                    Game.id.in_(
                        select(GameMember.game_id).join(
                            GameMember, GameMember.user_id == user_id
                        )
                    ),
                ),
                User.id.not_in(
                    select(Review.to_user_id).where(
                        Review.from_user_id == user_id,
                        Review.receiver_type == ReviewReceiverTypeEnum.player.value,
                    )
                ),
            )
        )
        return (await session.execute(query)).scalars().all()
