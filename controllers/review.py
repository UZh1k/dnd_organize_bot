from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from controllers.crud import CRUD
from models import Review, ReviewStatistic


class ReviewController(CRUD):
    model = Review

    @classmethod
    def common_query(cls):
        return (
            super()
            .common_query()
            .options(
                joinedload(Review.from_user),
                joinedload(Review.to_user),
            )
        )

    @classmethod
    async def get_user_reviews(
        cls,
        user_id: int,
        session: AsyncSession,
        receiver_type: str | None = None,
        only_with_comments: bool = False,
    ) -> Sequence[Review]:
        query = (
            cls.common_query()
            .where(Review.to_user_id == user_id)
            .order_by(Review.created.desc())
        )
        if receiver_type is not None:
            query = query.where(Review.receiver_type == receiver_type)
        if only_with_comments:
            query = query.where(Review.comment.is_not(None))

        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_reviews_statistic(
        cls, user_id: int, session: AsyncSession, receiver_type: str
    ) -> ReviewStatistic:
        reviews = await cls.get_user_reviews(user_id, session, receiver_type)
        total_count = len(reviews)

        rating_sum = 0
        comments_count = 0

        for review in reviews:
            if review.comment:
                comments_count += 1
            rating_sum += review.value

        return ReviewStatistic(
            total_count=total_count,
            rating=rating_sum / total_count if total_count else 0,
            comments_count=comments_count,
        )
