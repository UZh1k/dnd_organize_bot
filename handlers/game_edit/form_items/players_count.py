from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationPlayersCount


class GameEditPlayersCount(GameRegistrationPlayersCount):
    state = GameEditStates.players_count
