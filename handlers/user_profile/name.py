from handlers.user_profile.states import UserProfileStates
from handlers.user_registration import UserRegistrationName


class UserProfileName(UserRegistrationName):
    state = UserProfileStates.name
    prepare_text = (
        "Как игроки и мастера могут к тебе обращаться? "
        "Достаточно будет имени или никнейма. Отправь ответным сообщением."
    )