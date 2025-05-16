from operator import or_
from typing import Sequence

from sqlalchemy import select, Select, distinct, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from controllers.crud import CRUD
from models import Game, GameMember, ReviewMember
from models import Review, ReviewReceiverTypeEnum
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

    @classmethod
    async def get_user_ids_by_custom_filter(
        cls, custom_filter: str, session: AsyncSession
    ) -> Sequence[int]:
        query = select(User.id).where(text(custom_filter))
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_players_to_review(
        cls, user_id: int, session: AsyncSession, limit: int, page: int = 0
    ) -> tuple[Sequence[tuple[User, Game]], int]:
        query = (
            select(User, Game)
            .join(ReviewMember, User.id == ReviewMember.user_id)
            .join(Game, Game.id == ReviewMember.game_id)
            .where(
                User.registered.is_(True),
                or_(
                    Game.creator_id == user_id,
                    Game.id.in_(
                        select(ReviewMember.game_id).where(
                            ReviewMember.user_id == user_id
                        )
                    ),
                ),
                User.id != user_id,
                User.id.not_in(
                    select(Review.to_user_id).where(
                        Review.from_user_id == user_id,
                        Review.receiver_type == ReviewReceiverTypeEnum.player.value,
                    )
                ),
            )
        )
        paginated_query = (
            query.limit(limit).offset(page * limit).order_by(Game.id.desc())
        )
        total_count = await session.scalar(query.with_only_columns(func.count(User.id)))
        return (await session.execute(paginated_query)).all(), total_count
