import re

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from handlers.user_registration.states import UserRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem


class UserRegistrationTimezone(FormChoiceTextItem):
    state = UserRegistrationStates.timezone
    prepare_text = (
        'Выберите часовой пояс из списка или отправьте сообщение с данными '
        'своего UTC пояса, к примеру, "+1", "-5", "-3:30".'
    )
    form_name = "UserRegistration"
    form_item_name = "timezone"

    alert_message = "Часовой пояс сохранен"
    choices = (
        ("Калининградское МСК-1", "UTC+2"),
        ("Московское МСК", "UTC+3"),
        ("Самарское МСК+1", "UTC+4"),
        ("Екатеринбургское МСК+2", "UTC+5"),
        ("Омское МСК+3", "UTC+6"),
        ("Красноярское МСК+4", "UTC+7"),
        ("Иркутское МСК+5", "UTC+8"),
        ("Якутское МСК+6", "UTC+9"),
        ("Владивостокское МСК+7", "UTC+10"),
        ("Магаданское МСК+8", "UTC+11"),
        ("Камчатское МСК+9", "UTC+12"),
    )

    async def validate_answer(cls, message: Message, bot: AsyncTeleBot) -> bool:
        tz = message.text.replace("UTC", "")
        if not re.compile("^[+-][1-2]{0,1}[0-9](:30){0,1}$").match(tz):
            await bot.send_message(
                message.chat.id,
                "Это не похоже на часовой пояс, попробуй еще раз.",
            )
            return False
        return True

    async def save_answer(cls, text: str, user: User, session: AsyncSession):
        user.timezone = text if text.startswith("UTC") else f"UTC{text}"
