import re

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.user_registration.states import UserRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem


class UserRegistrationTimezone(FormChoiceTextItem):
    state = UserRegistrationStates.timezone
    prepare_text = (
        'Выбери часовой пояс из списка или отправь сообщение с данными своего '
        'UTC пояса, мне нужны только числа, например, "+1", "-5", "-3:30".'
    )
    form_item_name = "timezone"

    alert_message = "Часовой пояс сохранен"
    choices = (
        ("Калининградское МСК-1 (UTC+2)", "UTC+2"),
        ("Московское МСК (UTC+3)", "UTC+3"),
        ("Самарское МСК+1 (UTC+4)", "UTC+4"),
        ("Екатеринбургское МСК+2 (UTC+5)", "UTC+5"),
        ("Омское МСК+3 (UTC+6)", "UTC+6"),
        ("Красноярское МСК+4 (UTC+7)", "UTC+7"),
        ("Иркутское МСК+5 (UTC+8)", "UTC+8"),
        ("Якутское МСК+6 (UTC+9)", "UTC+9"),
        ("Владивостокское МСК+7 (UTC+10)", "UTC+10"),
        ("Магаданское МСК+8 (UTC+11)", "UTC+11"),
        ("Камчатское МСК+9 (UTC+12)", "UTC+12"),
    )

    async def validate_answer(cls, message: Message, bot: AsyncTeleBot) -> bool:
        tz = message.text.replace("UTC", "")
        if not re.compile("^[+-][1-2]{0,1}[0-9](:30){0,1}$").match(tz):
            await bot.send_message(
                message.chat.id,
                "Не смог разобрать твой ответ, пожалуйста, "
                "попробуй написать по-другому",
            )
            return False
        return True

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        user.timezone = text if text.startswith("UTC") else f"UTC{text}"
