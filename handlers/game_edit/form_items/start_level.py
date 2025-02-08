from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationStartLevel


class GameEditStartLevel(GameRegistrationStartLevel):
    state = GameEditStates.start_level
