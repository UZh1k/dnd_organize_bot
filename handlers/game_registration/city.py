from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from controllers.city import CityController
from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.other import generate_city_choices


class GameRegistrationCity(FormChoiceTextItem):
    state = GameRegistrationStates.city
    prepare_text = (
        "В каком городе ты хочешь провести игру? Выбери город из списка или "
        "напиши текстом название, если твоего города нет в списке."
    )
    form_name = "GameRegistration"
    form_item_name = "city"

    alert_message = "Город сохранен"
    choices = generate_city_choices()

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if message.text.isdigit() or len(message.text) > 100:
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
        city = await CityController.get_or_create(text, "name", session)
        await state.add_data(city_id=city.id)
