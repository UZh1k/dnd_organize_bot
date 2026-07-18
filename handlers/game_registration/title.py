from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class GameRegistrationTitle(FormTextItem):
    state = GameRegistrationStates.title
    message_length = 80
    prepare_text = (
        "Придумай короткое название для твоей игры. "
        "Напиши мне ответ в свободной форме.\n\n"
        f"Пожалуйста, постарайся уместиться в {message_length} символов. "
        f"Это обусловлено ограничениями самого мессенджера, "
        f"посты не могут превышать определенной длины."
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(title=text)
