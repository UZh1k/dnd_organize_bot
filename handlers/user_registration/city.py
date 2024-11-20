from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from controllers.city import CityController
from handlers.user_registration.states import UserRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem


class UserRegistrationCity(FormChoiceTextItem):
    state = UserRegistrationStates.city
    prepare_text = (
        "Теперь город. Выбери из кнопок или напиши ссообщением, "
        "если твоего города в списке нет"
    )
    form_name = "UserRegistration"
    form_item_name = "city"

    alert_message = "Город сохранен"
    choices = (
        ("Москва", "Москва"),
        ("Санкт-Петербург", "Санкт-Петербург"),
        ("Казань", "Казань"),
        ("Новосибирск", "Новосибирск"),
        ("Владивосток", "Владивосток"),
    )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if message.text.isdigit() or len(message.text) > 100:
            await bot.send_message(
                message.chat.id,
                "Это не похоже на название города, попробуй еще раз.",
            )
            return False
        return True

    async def save_answer(self, text: str, user: User, session: AsyncSession):
        city = await CityController.get_or_create(text, "name", session)
        user.city_id = city.id
