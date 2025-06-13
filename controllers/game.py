from typing import Sequence

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from controllers.crud import CRUD
from models import Game, Review, ReviewReceiverTypeEnum, ReviewMember, GameTagLink


class GameController(CRUD):
    model = Game

    @classmethod
    def common_query(cls):
        return select(cls.model).options(
            joinedload(Game.city), selectinload(Game.tags), joinedload(Game.creator)
        )

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

    @classmethod
    async def get_games_to_review(
        cls, user_id: int, session: AsyncSession, limit: int = 19, page: int = 0
    ) -> tuple[Sequence[Game], int]:
        query = (
            select(Game)
            .join(ReviewMember, ReviewMember.game_id == Game.id)
            .options(joinedload(Game.creator))
            .where(
                ReviewMember.user_id == user_id,
                Game.creator_id.not_in(
                    select(Review.to_user_id).where(
                        Review.from_user_id == user_id,
                        Review.receiver_type == ReviewReceiverTypeEnum.dm,
                    )
                ),
            )
        )
        paginated_query = (
            query.limit(limit).offset(page * limit).order_by(Game.id.desc())
        )
        total_count = await session.scalar(query.with_only_columns(func.count(Game.id)))
        return (await session.execute(paginated_query)).scalars().all(), total_count

    @classmethod
    async def search_one(
        cls,
        session: AsyncSession,
        offset: int = 0,
        tags: list[int] | None = None,
        **filters
    ) -> tuple[Game | None, int]:
        query = cls.common_query()

        set_filters = {
            key: value for key, value in filters.items() if value is not None
        }
        query = query.where(Game.active.is_(True), Game.post_id.is_not(None)).filter_by(
            **set_filters
        )

        if tags:
            query = query.where(
                Game.id.in_(
                    select(GameTagLink.game_id)
                    .where(GameTagLink.tag_id.in_(tags))
                    .group_by(GameTagLink.game_id)
                    .having(func.count(func.distinct(GameTagLink.tag_id)) == len(tags))
                )
            )

        count = await session.scalar(query.with_only_columns(func.count(Game.id)))
        if not count:
            return None, count

        query = query.offset(offset).limit(1).order_by(Game.last_update.desc())
        game = (await session.execute(query)).scalar_one_or_none()
        return game, count
