from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.controllers.city import CityController
from src.handlers.user_registration.timezone import UserRegistrationTimezone
from src.handlers.user_registration.states import UserRegistrationStates
from src.models import User
from src.utils.form.form_choice_text_item import FormChoiceTextItem
from src.utils.other import generate_city_choices, CITY_TO_TIMEZONE


class UserRegistrationCity(FormChoiceTextItem):
    state = UserRegistrationStates.city
    prepare_text = (
        "В каком городе ты живешь? Выбери город из списка или напиши текстом название, "
        "если твоего города нет в списке."
    )
    form_item_name = "city"
    message_length = 30

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
        await session.flush()

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        if known_timezone := CITY_TO_TIMEZONE.get(answer):
            user.timezone = known_timezone
            await self.next_step(chat_id, user, session, bot, state, self.form_prefix)
        else:
            await UserRegistrationTimezone.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
