from handlers.review.choose_game import ReviewChooseGameHandler
from handlers.review.choose_player import ReviewChoosePlayerHandler
from handlers.review.rate_number import RateNumberHandler
from handlers.review.menu import ReviewMenuHandler
from handlers.review.menu_create_review import MenuCreateReviewHandler
from handlers.review.menu_edit_reviews import MenuEditReviewHandler
from handlers.review.rate import ReviewRateHandler
from handlers.review.read_review import ReadReviewHandler
from handlers.review.review_item import ReviewItemHandler
from handlers.review.review_item_delete import ReviewItemDeleteHandler
from handlers.review.review_item_delete_clarify import ReviewItemDeleteClarifyHandler
from handlers.review.review_item_ok import ReviewItemOkHandler
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
        MenuCreateReviewHandler,
        MenuEditReviewHandler,
        ReviewItemOkHandler,
        ReviewItemDeleteClarifyHandler,
        ReviewItemDeleteHandler,
        ReviewItemHandler,
    ]
