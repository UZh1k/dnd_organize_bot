from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form import FormTextItem


class GameRegistrationTime(FormTextItem):
    state = GameRegistrationStates.time
    prepare_text = (
        "Когда ты планируешь провести игру? Есть конкретное время и дата? "
        "Может дни недели? При написании времени укажи, пожалуйста, часовой пояс. "
        "Напиши мне ответ в свободной форме."
    )
    message_length = 50

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(time=text)
