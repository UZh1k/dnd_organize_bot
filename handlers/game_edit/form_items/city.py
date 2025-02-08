from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationCity


class GameEditCity(GameRegistrationCity):
    state = GameEditStates.city
