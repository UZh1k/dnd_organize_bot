from enum import Enum

from telebot.states import StatesGroup, State

REVIEW_CALLBACK_PREFIX = "Review"
REVIEW_MENU_PREFIX = "review_menu"
REVIEW_CHOOSE_GAME_PREFIX = "review_dm"
RATE_STAGE = "rate_stage"

class ReviewMenuChoices(Enum):
    review_player = "review_player"
    review_dm = "review_dm"
    reviews_about_me = "reviews_about_me"


class ReviewStates(StatesGroup):
    review_player = State()
    review_dm = State()
    write_review = State()
