from typing import Sequence

from sqlalchemy import and_, exists, or_, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from controllers.crud import CRUD
from models import (
    Game,
    GameTagLink,
    Review,
    ReviewMember,
    ReviewReceiverTypeEnum,
    User,
)


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
    async def get_active_games_count(
        cls,
        creator_id: int,
        session: AsyncSession,
        lock_creator: bool = False,
    ) -> int:
        if lock_creator:
            await session.execute(
                select(User.id).where(User.id == creator_id).with_for_update()
            )
        query = select(func.count(Game.id)).where(
            Game.creator_id == creator_id,
            Game.active.is_(True),
            Game.group_id.is_not(None),
        )
        return (await session.scalar(query)) or 0

    @classmethod
    async def unlink_game_from_group(cls, group_id: int, session: AsyncSession):
        await session.execute(
            update(Game).where(Game.group_id == group_id).values(group_id=None)
        )

    @classmethod
    async def get_games_for_edit(
        cls,
        creator_id: int,
        session: AsyncSession,
        limit: int,
        page: int = 0,
    ) -> tuple[Sequence[Game], int]:
        filters = (
            Game.creator_id == creator_id,
            Game.active.is_(True),
        )
        total_count = await session.scalar(
            select(func.count(Game.id)).where(*filters)
        )
        query = (
            select(Game)
            .where(*filters)
            .order_by(Game.id)
            .limit(limit)
            .offset(page * limit)
        )
        games = (await session.execute(query)).scalars().all()
        return games, total_count or 0

    @classmethod
    async def get_games_to_review(
        cls, user_id: int, session: AsyncSession, limit: int = 19, page: int = 0
    ) -> tuple[Sequence[Game], int]:
        existing_review = exists(
            select(Review.id).where(
                Review.from_user_id == user_id,
                Review.to_user_id == Game.creator_id,
                Review.receiver_type == ReviewReceiverTypeEnum.dm,
            )
        )
        comment_without_rating = exists(
            select(Review.id).where(
                Review.from_user_id == user_id,
                Review.to_user_id == Game.creator_id,
                Review.receiver_type == ReviewReceiverTypeEnum.dm,
                Review.value.is_(None),
            )
        )
        query = (
            select(Game)
            .join(ReviewMember, ReviewMember.game_id == Game.id)
            .options(joinedload(Game.creator))
            .where(
                ReviewMember.user_id == user_id,
                or_(
                    ~existing_review,
                    and_(Game.done.is_(True), comment_without_rating),
                ),
            )
        )
        paginated_query = (
            query.limit(limit).offset(page * limit).order_by(Game.id.desc())
        )
        total_count = await session.scalar(query.with_only_columns(func.count(Game.id)))
        return (await session.execute(paginated_query)).scalars().all(), total_count

    @classmethod
    async def get_game_for_review(
        cls,
        from_user_id: int,
        to_user_id: int,
        receiver_type: ReviewReceiverTypeEnum,
        session: AsyncSession,
    ) -> Game | None:
        reviewer_membership = exists(
            select(ReviewMember.user_id).where(
                ReviewMember.game_id == Game.id,
                ReviewMember.user_id == from_user_id,
            )
        )

        if receiver_type == ReviewReceiverTypeEnum.dm:
            query = select(Game).where(
                Game.creator_id == to_user_id,
                reviewer_membership,
            )
        else:
            receiver_membership = exists(
                select(ReviewMember.user_id).where(
                    ReviewMember.game_id == Game.id,
                    ReviewMember.user_id == to_user_id,
                )
            )
            query = select(Game).where(
                receiver_membership,
                or_(Game.creator_id == from_user_id, reviewer_membership),
            )

        query = query.order_by(Game.done.desc().nulls_last(), Game.id.desc()).limit(1)
        return (await session.execute(query)).scalar_one_or_none()

    @classmethod
    async def search_one(
        cls,
        session: AsyncSession,
        offset: int = 0,
        tags: list[int] | None = None,
        **filters
    ) -> tuple[Game | None, int]:
        query = cls.common_query()

        column_names = [column.name for column in Game.__table__.columns]
        set_filters = {
            key: value
            for key, value in filters.items()
            if value is not None and key in column_names
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
