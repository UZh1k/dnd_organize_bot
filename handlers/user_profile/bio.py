from handlers.user_profile.states import UserProfileStates
from handlers.user_registration import UserRegistrationBio


class UserProfileBio(UserRegistrationBio):
    state = UserProfileStates.bio
    prepare_text = (
        "Расскажи немного о себе. Как давно ты играешь или "
        "ведешь игры? Какие системы тебе нравятся? Какими вселенными увлекаешься? "
        "Напиши мне ответ в свободной форме. Ответ станет твоим описанием."
    )
