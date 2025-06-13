from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.game_registration.redaction_and_setting import (
    GameRegistrationRedactionAndSetting,
)
from handlers.game_registration.dnd_redaction import GameRegistrationDndRedaction
from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.other import POPULAR_SYSTEMS_MAP


class GameRegistrationSystem(FormChoiceTextItem):
    state = GameRegistrationStates.system
    prepare_text = (
        "По какой игровой системе ты будешь проводить игру? "
        "Выбери из списка или напиши текстом, если твоей системы нет."
    )
    form_item_name = "system"
    message_length = 40

    alert_message = "Формат игры записан"
    choices = tuple((value, key) for key, value in POPULAR_SYSTEMS_MAP.items())

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        result = POPULAR_SYSTEMS_MAP.get(text, text)
        await state.add_data(system=result)

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
        if answer == "DnD":
            await GameRegistrationDndRedaction.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
        else:
            await GameRegistrationRedactionAndSetting.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
