from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from src.handlers.game_registration.states import GameRegistrationStates
from src.models import GameType, User
from src.utils.form.form_choice_item import FormChoiceItem


class GameRegistrationType(FormChoiceItem):
    state = GameRegistrationStates.type
    prepare_text = "Это будет Кампания или Ваншот?"
    form_item_name = "type"

    alert_message = "Тип игры записан"
    choices = (
        ("Кампания", "company"),
        ("Ваншот", "one_shot"),
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(type=GameType[text].value)
