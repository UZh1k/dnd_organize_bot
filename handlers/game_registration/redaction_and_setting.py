from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class GameRegistrationRedactionAndSetting(FormTextItem):
    state = GameRegistrationStates.redaction_and_setting
    prepare_text = (
        "По какой редакции и в каком сеттинге будет твоя игра? "
        "Пришли текст в ответном сообщении."
    )
    message_length = 40

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(redaction=text, setting=text)
