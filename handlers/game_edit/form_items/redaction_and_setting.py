from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationRedactionAndSetting


class GameEditRedactionAndSetting(GameRegistrationRedactionAndSetting):
    state = GameEditStates.redaction_and_setting
