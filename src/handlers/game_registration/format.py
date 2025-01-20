from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from src.handlers.game_registration.accept_offline import GameRegistrationAcceptOffline
from src.handlers.game_registration.states import GameRegistrationStates
from src.models import User, GameFormat
from src.utils.form.form_choice_item import FormChoiceItem


class GameRegistrationFormat(FormChoiceItem):
    state = GameRegistrationStates.format
    prepare_text = "В каком формате хочешь провести игру?"
    form_item_name = "format"

    alert_message = "Формат игры записан"
    choices = (
        ("Онлайн", GameFormat.online.name),
        ("Оффлайн", GameFormat.offline.name),
        ("Текстовая игра", GameFormat.text.name),
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(format=GameFormat[text].value)

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        if answer == "offline":
            await GameRegistrationAcceptOffline.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
        else:
            await self.next_step(chat_id, user, session, bot, state, self.form_prefix)

