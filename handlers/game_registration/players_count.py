from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.other import generate_simple_choices


class GameRegistrationPlayersCount(FormChoiceTextItem):
    state = GameRegistrationStates.players_count
    prepare_text = (
        "Сколько игроков потребуется для твоей игры? Выбери из списка или "
        "пришли ответ текстом в формате числа или двух чисел через дефис. "
        "Примеры: “4”, “3-5”, “6”."
    )
    form_name = "GameRegistration"
    form_item_name = "players_count"

    alert_message = "Количество игроков записано"
    choices = generate_simple_choices(
        ("1", "2", "3", "4", "5", "6", "2-3", "3-4", "4-5", "4-6")
    )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        async def with_false() -> bool:
            await bot.send_message(
                message.chat.id,
                "Не смог разобрать твой ответ, пожалуйста, "
                "попробуй написать по-другому",
            )
            return False

        if message.text.isdigit():
            min_players = max_players = int(message.text)
        elif len(message_split := message.text.split("-")) != 2:
            return await with_false()
        else:
            min_players_str, max_players_str = message_split
            if not min_players_str.isdigit() or not max_players_str.isdigit():
                return await with_false()
            else:
                min_players = int(min_players_str)
                max_players = int(max_players_str)

        if min_players > 20 or max_players > 20 or min_players > max_players:
            return await with_false()
        return True

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        if text.isdigit():
            min_players = max_players = int(text)
        else:
            min_players, max_players = map(int, text.split("-"))
        await state.add_data(min_players=min_players, max_players=max_players)
