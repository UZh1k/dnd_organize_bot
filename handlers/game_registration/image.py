from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_photo_item import FormPhotoItem


class GameRegistrationImage(FormPhotoItem):
    state = GameRegistrationStates.image
    prepare_text = "Пришли, пожалуйста, картинку, которая станет обложкой твоей игры."

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        await bot.send_message(
            message.chat.id, "Это должна быть именно картинка, попробуй еще раз"
        )
        return False

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(image=text)
