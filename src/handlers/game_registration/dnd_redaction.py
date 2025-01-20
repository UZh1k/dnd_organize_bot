from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from src.handlers.game_registration.dnd_setting import GameRegistrationDndSetting
from src.handlers.game_registration.states import GameRegistrationStates
from src.models import User
from src.utils.form.form_choice_item import FormChoiceItem
from src.utils.other import generate_simple_choices, POPULAR_DND_REDACTIONS


class GameRegistrationDndRedaction(FormChoiceItem):
    state = GameRegistrationStates.dnd_redaction
    prepare_text = "По какой редакции DnD будет твоя игра? Выбери из списка."
    form_item_name = "dnd_redaction"

    alert_message = None
    choices = generate_simple_choices(POPULAR_DND_REDACTIONS)

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(redaction=text)

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await GameRegistrationDndSetting.prepare(
            chat_id, user, session, bot, state, self.form_prefix
        )
