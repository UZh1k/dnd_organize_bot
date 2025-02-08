from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationTechRequirements


class GameEditTechRequirements(GameRegistrationTechRequirements):
    state = GameEditStates.tech_requirements
