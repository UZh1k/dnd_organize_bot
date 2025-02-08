from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationTag


class GameEditTag(GameRegistrationTag):
    state = GameEditStates.tag
