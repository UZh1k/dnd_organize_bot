from handlers.game_edit.settings import GameEditStates
from handlers.game_registration.platform import GameRegistrationPlatform


class GameEditPlatform(GameRegistrationPlatform):
    state = GameEditStates.platform
