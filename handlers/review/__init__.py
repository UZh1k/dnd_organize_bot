from handlers.review.choose_game import ReviewChooseGameHandler
from handlers.review.choose_player import ReviewChoosePlayerHandler
from handlers.review.handle_rate import RateNumberHandler
from handlers.review.menu import ReviewMenuHandler
from handlers.review.rate import ReviewRateHandler
from handlers.review.read_review import ReadReviewHandler
from handlers.review.save_review import SaveReviewHandler
from utils.handler_groups.base_handler_group import BaseHandlerGroup


class ReviewHandlerGroup(BaseHandlerGroup):
    handlers = [
        ReviewChooseGameHandler,
        ReviewChoosePlayerHandler,
        RateNumberHandler,
        ReviewMenuHandler,
        ReviewRateHandler,
        SaveReviewHandler,
        ReadReviewHandler,
    ]
