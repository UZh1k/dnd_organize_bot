from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_item import FormChoiceItem
from utils.other import generate_simple_choices


class GameRegistrationDndRedaction(FormChoiceItem):
    state = GameRegistrationStates.dnd_redaction
    prepare_text = "По какой редакции DnD будет твоя игра? Выбери из списка."
    form_name = "GameRegistration"
    form_item_name = "dnd_redaction"

    alert_message = None
    choices = generate_simple_choices(
        ("DnD24", "DnD5e", "DnD3.5e", "DnD3e", "DnD2e", "ADnD", "ODnD")
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(redaction=text)
