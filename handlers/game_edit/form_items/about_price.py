from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationAboutPrice


class GameEditAboutPrice(GameRegistrationAboutPrice):
    state = GameEditStates.about_price
