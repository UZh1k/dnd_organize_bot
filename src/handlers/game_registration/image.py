from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.handlers.game_registration.states import GameRegistrationStates
from src.models import User
from src.utils.form.form_photo_item import FormPhotoItem


class GameRegistrationImage(FormPhotoItem):
    state = GameRegistrationStates.image
    prepare_text = (
        "Пришли, пожалуйста, картинку, которая станет обложкой твоей игры. "
        "Размер картинки не должен превышать 2 МБ, формат должен быть jpg, "
        "jpeg, png. Важно прислать картинку не файлом, а картинкой и быстрой "
        "отправкой."
    )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if not message.photo:
            await bot.send_message(
                message.chat.id,
                "Не смог сохранить твою картинку, пожалуйста, "
                "проверь размер файла или формат. Если у тебя нет программ, "
                "то попробуй онлайн конвертеры картинок. Важно прислать "
                "картинку не файлом, а картинкой и быстрой отправкой.",
            )
            return False
        return True

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(image=text)
