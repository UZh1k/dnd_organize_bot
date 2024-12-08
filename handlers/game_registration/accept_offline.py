from handlers.game_registration.states import GameRegistrationStates
from utils.form.form_choice_item import FormChoiceItem


class GameRegistrationAcceptOffline(FormChoiceItem):
    state = GameRegistrationStates.accept_offline
    prepare_text = (
        "Я тебя предупреждаю, что реальный мир может быть также опасен, "
        "как и мир НРИ. Пожалуйста, не встречайся с незнакомцами на "
        "игры из дома. Можно собираться только в публичных местах. "
        "Это очень важно!"
    )
    form_name = "GameRegistration"
    form_item_name = "accept_offline"

    alert_message = None
    choices = (("Я понял", "Ok"),)
