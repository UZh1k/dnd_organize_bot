from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationType


class GameEditType(GameRegistrationType):
    state = GameEditStates.type
