from handlers.user_registration.states import UserRegistrationStates
from utils.form.form_choice_item import FormChoiceItem


class UserRegistrationAcceptMinor(FormChoiceItem):
    state = UserRegistrationStates.accept_minor
    prepare_text = (
        "Я тебя предупреждаю, что реальный мир может быть также опасен, "
        "как и мир НРИ. Пожалуйста, не встречайся ни с кем на игры дома. "
        "Можно собираться только в публичных местах или в онлайне. Это очень важно!"
    )
    form_name = "UserRegistration"
    form_item_name = "accept_minor"

    alert_message = None
    choices = (
        ("Я понял", "accept"),
    )
