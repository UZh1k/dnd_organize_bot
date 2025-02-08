from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationTime


class GameEditTime(GameRegistrationTime):
    state = GameEditStates.time
