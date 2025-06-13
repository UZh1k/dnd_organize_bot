from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.game_registration.description import GameRegistrationDescription
from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.other import generate_simple_choices, POPULAR_DND_SETTINGS


class GameRegistrationDndSetting(FormChoiceTextItem):
    state = GameRegistrationStates.dnd_setting
    prepare_text = (
        "В каком сеттинге DnD будет твоя игра? Выбери из списка или "
        "напиши ответ в текстовом сообщении."
    )
    form_item_name = "dnd_setting"
    message_length = 40

    alert_message = None
    choices = generate_simple_choices(POPULAR_DND_SETTINGS)

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(setting=text)

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        **kwargs,
    ):
        await GameRegistrationDescription.prepare(
            chat_id, user, session, bot, state, self.form_prefix
        )
