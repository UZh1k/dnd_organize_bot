import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_storage import StateMemoryStorage
from telebot.states.asyncio import StateMiddleware
from telebot.states.asyncio.context import StateContext
from telebot.types import (
    Message,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from consts import BOT_TOKEN, ENVIRONMENT, NEWS_CHANNEL_ID, BOT_USERNAME
from controllers.game import GameController
from handlers.game_application import GameApplicationHandler
from handlers.game_application.states import GameApplicationStates
from handlers.game_registration.states import GameRegistrationStates
from handlers.group_administration import GroupAdministrationHandler
from handlers.user_registration import UserRegistrationHandler
from middlewares.session import SessionMiddleware
from middlewares.user import UserMiddleware
from models import Game
from models.user import User
from utils.message_helpers import send_message_with_link_button

state_storage = StateMemoryStorage() if ENVIRONMENT == "local" else None
bot = AsyncTeleBot(BOT_TOKEN, state_storage=state_storage)


@bot.message_handler(
    commands=["start"], func=lambda message: len(message.text.split()) == 1
)
async def handle_start(message: Message, session: AsyncSession, user: User):
    await bot.send_message(message.chat.id, "hello there")


@bot.message_handler(commands=["help", "about"])
async def send_welcome(message: Message, session: AsyncSession, user: User):
    text = "hello there"
    await bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["find_game"], chat_types="private")
async def find_game(message: Message, session: AsyncSession, user: User):
    invite_link = await bot.export_chat_invite_link(NEWS_CHANNEL_ID)
    await send_message_with_link_button(
        bot,
        message.chat.id,
        "TBD Зайди в канал с играми, только лучше сначала зарегистрируйся",
        "TBD Канал с играми",
        invite_link,
    )


@bot.message_handler(commands=["new_game"], chat_types="private")
async def create_new_game(
    message: Message, session: AsyncSession, user: User, state: StateContext
):
    if user.registered:
        await state.set(GameRegistrationStates.title)
        await bot.send_message(message.chat.id, "Напиши название игры")
    else:
        await bot.send_message(
            message.chat.id, "Сначала пройди регистрацию через /register"
        )


@bot.message_handler(state=GameRegistrationStates.title)
async def set_title(
    message: Message, session: AsyncSession, user: User, state: StateContext
):
    game = Game(
        creator_id=user.id, title=message.text, description=message.text, active=True
    )
    session.add(game)
    await bot.send_message(message.chat.id, "Теперь добавь бота в новую группу")


UserRegistrationHandler(bot).register_handlers()
GroupAdministrationHandler(bot).register_handlers()
GameApplicationHandler(bot).register_handlers()

bot.add_custom_filter(StateFilter(bot))

bot.setup_middleware(SessionMiddleware())
bot.setup_middleware(UserMiddleware())
bot.setup_middleware(StateMiddleware(bot))

if __name__ == "__main__":
    asyncio.run(bot.infinity_polling())
