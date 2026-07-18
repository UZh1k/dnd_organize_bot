from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.other import generate_simple_choices, POPULAR_PLATFORMS


class GameRegistrationPlatform(FormChoiceTextItem):
    state = GameRegistrationStates.platform
    message_length = 30
    prepare_text = (
        "На какой онлайн площадке хочешь провести игру? Выбери площадке из списка "
        "или напиши текстом название, если нужной нет в списке.\n\n"
        f"Пожалуйста, постарайся уместиться в {message_length} символов. "
        f"Это обусловлено ограничениями самого мессенджера, "
        f"посты не могут превышать определенной длины."
    )
    form_item_name = "platform"

    alert_message = "Площадка сохранена"
    choices = generate_simple_choices(POPULAR_PLATFORMS)

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(platform=text)
