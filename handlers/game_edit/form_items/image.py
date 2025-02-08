from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationImage


class GameEditImage(GameRegistrationImage):
    state = GameEditStates.image
