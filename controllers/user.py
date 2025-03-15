from typing import Sequence

from sqlalchemy import select, Select, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from controllers.crud import CRUD
from models import Game, GameMember
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
    def _get_query_all(cls) -> Select:
        return select(User.id).where(User.banned.is_(False))

    @classmethod
    def _get_query_successful_dms(cls, free: bool | None = None) -> Select:
        query = (
            select(distinct(User.id))
            .join(Game, Game.creator_id == User.id)
            .where(Game.done.is_(True))
        )
        if free is not None:
            query = query.where(Game.free.is_(free))
        return query

    @classmethod
    def _get_query_players(cls):
        return (
            select(distinct(User.id))
            .join(GameMember, GameMember.user_id == User.id)
            .join(Game, Game.id == GameMember.game_id)
            .where(Game.done.is_(True))
        )

    @classmethod
    async def get_user_ids_to_send_notifications(
        cls, notification_type: str, session: AsyncSession
    ) -> Sequence[int]:
        map_query = {
            "to_paid_dms": cls._get_query_successful_dms(free=False),
            "to_free_dms": cls._get_query_successful_dms(free=True).where(
                User.id.not_in(cls._get_query_successful_dms(free=False))
            ),
            "to_players": cls._get_query_players().where(
                User.id.not_in(cls._get_query_successful_dms())
            ),
            "to_all": cls._get_query_all(),
        }

        result = await session.execute(map_query[notification_type])
        return result.scalars().all()
