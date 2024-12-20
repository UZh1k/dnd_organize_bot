from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class GameRegistrationTime(FormTextItem):
    state = GameRegistrationStates.time
    prepare_text = (
        "Когда ты планируешь провести игру? Есть конкретное время и дата? "
        "Может дни недели? При написании времени укажи, пожалуйста, часовой пояс. "
        "Напиши мне ответ в свободной форме."
    )
    message_length = 40

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(time=text)
