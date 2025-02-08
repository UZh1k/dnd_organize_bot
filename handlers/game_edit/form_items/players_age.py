from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationPlayersAge


class GameEditPlayersAge(GameRegistrationPlayersAge):
    state = GameEditStates.players_age
