from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form import FormTextItem


class GameRegistrationDescription(FormTextItem):
    state = GameRegistrationStates.description
    prepare_text = (
        "Дай описание своей кампании. Что ждет игроков? С какими опасностями они "
        "столкнутся? Игра будет динамичной или детективной, мистической или геройской? "
        "Раскажи подробнее. Напиши мне ответ в свободной форме."
    )
    message_length = 600

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(description=text)
