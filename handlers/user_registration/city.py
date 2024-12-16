from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from controllers.city import CityController
from handlers.user_registration.states import UserRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.other import generate_city_choices


class UserRegistrationCity(FormChoiceTextItem):
    state = UserRegistrationStates.city
    prepare_text = (
        "В каком городе ты живешь? Выбери город из списка или напиши текстом название, "
        "если твоего города нет в списке."
    )
    form_name = "UserRegistration"
    form_item_name = "city"
    message_length = 100

    alert_message = "Город сохранен"
    choices = generate_city_choices()

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if await self.check_is_not_digit(message, bot):
            return await super().validate_answer(message, bot)
        return False

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        city = await CityController.get_or_create(text, "name", session)
        user.city_id = city.id
