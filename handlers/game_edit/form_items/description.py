from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationDescription


class GameEditDescription(GameRegistrationDescription):
    state = GameEditStates.description
