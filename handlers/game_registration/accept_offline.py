from handlers.game_registration.states import GameRegistrationStates
from utils.form.form_choice_item import FormChoiceItem


class GameRegistrationAcceptOffline(FormChoiceItem):
    state = GameRegistrationStates.accept_offline
    prepare_text = (
        "Я тебя предупреждаю, что реальный мир может быть также опасен, "
        "как и мир НРИ. Пожалуйста, не собирайся на игры, если их проводят "
        "дома и сам не приглашай никого к себе домой. Можно собираться только "
        "в публичных местах или в онлайне. Это очень важно!"
    )
    form_name = "GameRegistration"
    form_item_name = "accept_offline"

    alert_message = None
    choices = (("Я понял", "Ok"),)
