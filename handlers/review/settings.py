from enum import Enum

from telebot.states import StatesGroup, State

REVIEW_CALLBACK_PREFIX = "Review"
REVIEW_MENU_PREFIX = "review_menu"
REVIEW_ITEM_PREFIX = "review_item"
RATE_STAGE = "rate_stage"
EMPTY_CALLBACK = "comment:empty"


class ReviewMenuChoices(Enum):
    review_player = "review_player"
    review_dm = "review_dm"
    reviews_about_me = "reviews_about_me"
    create_review = "create_review"
    edit_review = "edit_review"
    menu = "menu"


class ReviewItemMenuChoices(Enum):
    delete = "delete"
    delete_clarify = "delete_clarify"
    ok = "ok"


class ReviewStates(StatesGroup):
    review = State()
    write_comment = State()
