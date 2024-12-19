from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.user_registration.states import UserRegistrationStates
from models import User, UserType
from utils.form.form_choice_item import FormChoiceItem


class UserRegistrationUserType(FormChoiceItem):
    state = UserRegistrationStates.user_type
    prepare_text = "Какая у тебя роль в НРИ?"
    form_item_name = "user_type"

    alert_message = "Ответ сохранен"
    choices = (
        ("Игрок", "player"),
        ("Мастер Игры", "dm"),
        ("Игрок и Мастер Игры", "both"),
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        user.user_type = UserType[text].value
