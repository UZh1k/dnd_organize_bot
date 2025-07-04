import asyncio
import logging

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_storage import StateMemoryStorage, StateRedisStorage
from telebot.states.asyncio import StateMiddleware
from telebot.states.asyncio.context import StateContext
from telebot.types import Message, Update

from consts import (
    BOT_TOKEN,
    ALLOWED_UPDATE_TYPES,
    START_IMAGE,
    BOOSTY_LINK,
    CRYPTO_LINK,
    WEBHOOK_URL_PATH,
    STATE_STORAGE,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASS,
)
from handlers.administration import AdministrationHandlerGroup
from handlers.feedback import FeedbackHandlerGroup
from handlers.filters import FiltersHandlerGroup
from handlers.game_application import GameApplicationHandlerGroup
from handlers.game_edit import GameEditHandlerGroup
from handlers.game_registration import GameRegistrationHandlerGroup
from handlers.group_administration import GroupAdministrationHandlerGroup
from handlers.review import ReviewHandlerGroup
from handlers.user_profile import UserProfileHandlerGroup
from handlers.user_registration import UserRegistrationHandlerGroup
from middlewares.exception import ExceptionMiddleware
from middlewares.session import SessionMiddleware
from middlewares.user import UserMiddleware
from models.user import User
from utils.message_helpers import send_message_with_link_button, get_channel_link

state_storage = (
    StateRedisStorage(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
    if STATE_STORAGE == "redis"
    else StateMemoryStorage()
)
bot = AsyncTeleBot(BOT_TOKEN, state_storage=state_storage)


app = FastAPI()


@app.post(WEBHOOK_URL_PATH)
async def process_webhook(update: dict):
    """
    Process webhook calls
    """
    if update:
        update = Update.de_json(update)
        await bot.process_new_updates([update])
    else:
        return


@app.get("/up", status_code=200)
async def health():
    return {}


@bot.message_handler(
    commands=["start"],
    func=lambda message: len(message.text.split()) == 1,
    chat_types=["private"],
)
async def handle_start(
    message: Message, session: AsyncSession, user: User, state: StateContext
):
    await state.delete()
    text = (
        "Привет! Я Сники Бот! Давай помогу найти или создать игру "
        "по твоим любимым НРИ. Для начала тебе нужно зарегистрироваться. "
        "Сделать это очень просто и быстро. Нажми в меню слева внизу кнопку "
        "“Регистрация” или отправь команду /register. \n\n"
        "Если хочешь узнать побольше обо мне или поддержать мое развитие и "
        "сопровождение, то жми команду “О боте” или отправь /about.\n\n"
        "Если нашел ошибку или у тебя есть предложение по развитию, "
        "то жми команду /feedback.\n\n"
        "Если ты искал справочную информацию по ДНД 2024, то тебе лучше "
        "обратиться к Сники Справочнику - @sneaky_library_bot.\n\n"
        "Больше полезных материалов к ролевым играм ты "
        "найдёшь тут: https://t.me/sneaky_dice"
    )
    await send_message_with_link_button(
        bot,
        message.chat.id,
        text,
        "Канал с играми",
        await get_channel_link(bot),
        photo=START_IMAGE,
    )


@bot.message_handler(commands=["help", "about"], chat_types=["private"])
async def handle_about(
    message: Message, session: AsyncSession, user: User, state: StateContext
):
    await state.delete()
    text = (
        "Привет! Я Сники Бот! Для регистрации нажми в меню слева внизу кнопку "
        "“Регистрация” или отправь команду /register. Если ты уже зарегистрировался, "
        "то ты можешь начать подбор игроков через нажатие “Создание игры” или "
        "отправив команду /create, а найти игру через “Поиск игры” или "
        "команду /search.\n\n"
        "Если нашел ошибку или у тебя есть предложение по развитию, то жми команду  "
        "“Предложить исправление” или отправь /feedback.\n\n"
        "Я был создан небольшой командой энтузиастов. В меня вложили множество сил и "
        "времени, чтобы я мог появиться на свет. Мое существование, а также дальнейшее "
        "развитие зависит только от вас.\n\n"
        "У меня есть множество нереализованных идей, которые, как я надеюсь, "
        "вы сможете увидеть. Но на текущий момент я бы хотел, "
        "чтобы ваших донатов хватило хотя бы на мое ежемесячное сопровождение "
        "платного хостинга. Даже 100 рублей уже сильно мне помогут.\n\n"
        "Буду очень вам благодарен. Ваш Сники Бот.\n\n"
        f"• Бусти - {BOOSTY_LINK}\n"
        f"• Крипта - USDT (TRC20 | TRON) {CRYPTO_LINK} \n\n"
        f"Больше полезных материалов к ролевым играм ты найдёшь "
        f"тут: https://t.me/sneaky_dice"
    )
    await send_message_with_link_button(
        bot,
        message.chat.id,
        text,
        "Канал с играми",
        await get_channel_link(bot),
    )


@bot.message_handler(commands=["sneaky_library_bot"], chat_types="private")
async def library_bot(
    message: Message, session: AsyncSession, user: User, state: StateContext
):
    await state.delete()
    await bot.send_message(
        message.chat.id,
        "Если ты искал справочную информацию по ДНД 2024, "
        "то тебе лучше обратиться к Сники Справочнику - @sneaky_library_bot.",
    )


AdministrationHandlerGroup(bot).register_handlers()
GroupAdministrationHandlerGroup(bot).register_handlers()
FeedbackHandlerGroup(bot).register_handlers()
GameApplicationHandlerGroup(bot).register_handlers()
UserRegistrationHandlerGroup(bot).register_handlers()
UserProfileHandlerGroup(bot).register_handlers()
GameRegistrationHandlerGroup(bot).register_handlers()
GameEditHandlerGroup(bot).register_handlers()
ReviewHandlerGroup(bot).register_handlers()
FiltersHandlerGroup(bot).register_handlers()


@bot.message_handler(content_types=["text", "photo", "file"], chat_types=["private"])
async def any_text(
    message: Message, session: AsyncSession, user: User, state: StateContext
):
    await bot.send_message(
        message.chat.id,
        "Ты ввел сообщение, но я не понимаю твою команду. Пожалуйста, "
        "проверь команду или выбери ее в меню слева внизу. Список всех команд "
        "ты можешь посмотреть, отправив /about.",
    )


bot.add_custom_filter(StateFilter(bot))

bot.setup_middleware(SessionMiddleware())
bot.setup_middleware(UserMiddleware())
bot.setup_middleware(ExceptionMiddleware(bot))
bot.setup_middleware(StateMiddleware(bot))


if __name__ == "__main__":
    asyncio.run(
        bot.infinity_polling(
            allowed_updates=ALLOWED_UPDATE_TYPES, logger_level=logging.INFO
        )
    )
