import re

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.other import generate_simple_choices


class GameRegistrationPlayersAge(FormChoiceTextItem):
    state = GameRegistrationStates.players_age
    prepare_text = (
        "Какие у тебя требования к возрасту игроков? Выбери из списка или "
        "пришли ответ в формате двух чисел через дефис или одно число со "
        "знаком “+”. Примеры: “18-20”, “20-30”, “20+”."
    )
    form_item_name = "players_age"

    alert_message = "Требования по возрасту сохранены"
    choices = generate_simple_choices(("14+", "14-17", "18+", "18-25", "25+"))

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        async def with_false() -> bool:
            await bot.send_message(
                message.chat.id,
                "Не смог разобрать твой ответ, пожалуйста, "
                "попробуй написать по-другому",
            )
            return False

        if not re.compile(
            r"^(1[4-9]|[2-9][0-9])\s?(\+|-\s?(1[5-9]|[2-9][0-9]))$"
        ).match(message.text):
            return await with_false()

        if "-" in message.text:
            min_age, max_age = map(int, message.text.split("-"))
            if min_age > max_age:
                return await with_false()
        return True

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        if "-" in text:
            min_age, max_age = map(int, text.split("-"))
        else:
            min_age = int(text.replace("+", ""))
            max_age = None
        await state.add_data(min_age=min_age, max_age=max_age)
