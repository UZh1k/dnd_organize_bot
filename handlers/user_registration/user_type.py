from sqlalchemy.ext.asyncio import AsyncSession

from handlers.user_registration.states import RegistrationStates
from models import User, UserType
from utils.form_choice_item import FormChoiceItem


class UserRegistrationUserType(FormChoiceItem):
    state = RegistrationStates.user_type
    prepare_text = "Ты ДМ или игрок?"
    form_name = "UserRegistration"
    form_item_name = "user_type"

    alert_message = "Ответ сохранен"
    choices = (
        ("ДМ", "dm"),
        ("Игрок", "player"),
        ("И то, и то", "both"),
    )

    async def save_answer(cls, text: str, user: User, session: AsyncSession):
        user.user_type = UserType[text].value
