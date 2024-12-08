from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.user_registration.states import UserRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class UserRegistrationBio(FormTextItem):
    state = UserRegistrationStates.bio
    prepare_text = (
        "И последний вопрос. Расскажи немного о себе. Как давно ты играешь или "
        "ведешь игры? Какие системы тебе нравятся? Какими вселенными увлекаешься? "
        "Напиши мне ответ в свободной форме. Ответ станет твоим описанием."
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        user.bio = text
