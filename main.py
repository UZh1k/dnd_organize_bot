import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_storage import StateMemoryStorage
from telebot.states.asyncio import StateMiddleware
from telebot.states.asyncio.context import StateContext
from telebot.types import Message

from consts import BOT_TOKEN, ENVIRONMENT
from handlers.user_registration import UserRegistrationHandler
from middlewares.session import SessionMiddleware
from middlewares.user import UserMiddleware
from models.user import User

state_storage = StateMemoryStorage() if ENVIRONMENT == "local" else None
bot = AsyncTeleBot(BOT_TOKEN, state_storage=state_storage)


@bot.message_handler(commands=["help", "start", "about"])
async def send_welcome(message: Message, session: AsyncSession, user: User):
    text = "hello there"
    await bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["find_game"], chat_types="private")
async def find_game(message: Message, session: AsyncSession, user: User):
    ...

@bot.message_handler(commands=["new_game"], chat_types="private")
async def create_new_game(message: Message, session: AsyncSession, user: User):
    ...



UserRegistrationHandler(bot).register_handlers()

bot.add_custom_filter(StateFilter(bot))

bot.setup_middleware(SessionMiddleware())
bot.setup_middleware(UserMiddleware())
bot.setup_middleware(StateMiddleware(bot))

if __name__ == "__main__":
    asyncio.run(bot.infinity_polling())
