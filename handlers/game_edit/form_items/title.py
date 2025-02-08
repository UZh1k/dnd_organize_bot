from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationTitle


class GameEditTitle(GameRegistrationTitle):
    state = GameEditStates.title
