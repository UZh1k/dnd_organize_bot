from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.other import generate_simple_choices, POPULAR_SYSTEMS


class GameRegistrationSystem(FormChoiceTextItem):
    state = GameRegistrationStates.system
    prepare_text = (
        "По какой игровой системе ты будешь проводить игру? "
        "Выбери из списка или напиши текстом, если твоей системы нет."
    )
    form_name = "GameRegistration"
    form_item_name = "system"
    message_length = 50

    alert_message = "Формат игры записан"
    choices = generate_simple_choices(POPULAR_SYSTEMS)

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(system=text)
