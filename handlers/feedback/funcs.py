from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states import StatesGroup, State
from telebot.states.asyncio import StateContext
from telebot.types import Message, User

from consts import FEEDBACK_IMAGE, FEEDBACK_CHAT_ID


class FeedbackStates(StatesGroup):
    get_feedback = State()


async def handle_feedback(
    message: Message,
    bot: AsyncTeleBot,
    user: User,
    session: AsyncSession,
    state: StateContext,
):
    await bot.send_photo(
        message.chat.id,
        FEEDBACK_IMAGE,
        "Если ты хочешь предложить как меня улучшить или ты столкнулся "
        "с ошибкой в моем функционале, то отправь ответное сообщение. "
        "Если хочешь прислать скриншот или скринкас, "
        "то напиши сообщение вместе с отправкой "
        "файла, чтобы фидбек был отправлен одним сообщением. Спасибо!",
    )
    await state.set(FeedbackStates.get_feedback)


async def forward_to_admins(
    message: Message,
    bot: AsyncTeleBot,
    user: User,
    session: AsyncSession,
    state: StateContext,
):
    await bot.forward_message(FEEDBACK_CHAT_ID, message.chat.id, message.id)
    await bot.send_message(message.chat.id, "Фидбек отправлен")
    await state.delete()
