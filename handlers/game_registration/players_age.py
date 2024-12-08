from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.other import generate_simple_choices


class GameRegistrationPlayersAge(FormChoiceTextItem):
    state = GameRegistrationStates.players_count
    prepare_text = (
        "Какие у тебя требования к возрасту игроков? Выбери из списка или пришли "
        "ответ в формате двух чисел через дефис. Примеры: “18-20”, “20-30”."
    )
    form_name = "GameRegistration"
    form_item_name = "players_age"

    alert_message = "Требования по возрасту сохранены"
    choices = generate_simple_choices(
        ("14-17", "18-25", "18-30", "30-40")
    )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        async def with_false() -> bool:
            await bot.send_message(
                message.chat.id,
                "Не смог разобрать твой ответ, пожалуйста, "
                "попробуй написать по-другому",
            )
            return False

        if len(message_split := message.text.split("-")) != 2:
            return await with_false()
        else:
            min_age_str, max_age_str = message_split
            if not min_age_str.isdigit() or not max_age_str.isdigit():
                return await with_false()
            else:
                min_age = int(min_age_str)
                max_age = int(max_age_str)

        if min_age > 20 or max_age > 20:
            return await with_false()
        return True

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        min_age, max_age = map(int, text.split("-"))
        await state.add_data(min_age=min_age, max_age=max_age)
