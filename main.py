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
import src.consts
from src.handlers.administration import AdministrationHandlerGroup
from src.handlers.feedback import FeedbackHandlerGroup
from src.handlers.game_application import GameApplicationHandlerGroup
from src.handlers.game_registration import GameRegistrationHandlerGroup
from src.handlers.group_administration import GroupAdministrationHandlerGroup
from src.handlers.user_profile import UserProfileHandlerGroup
from src.handlers.user_registration import UserRegistrationHandlerGroup
from src.middlewares.exception import ExceptionMiddleware
from src.middlewares.session import SessionMiddleware
from src.middlewares.user import UserMiddleware
from src.models.user import User
from src.utils.message_helpers import send_message_with_link_button

state_storage = (
    StateRedisStorage(host=src.consts.REDIS_URL, port=src.consts.REDIS_PORT, password=src.consts.REDIS_PASS)
    if src.consts.STATE_STORAGE == "redis"
    else StateMemoryStorage()
)
bot = AsyncTeleBot(src.consts.BOT_TOKEN, state_storage=state_storage)


app = FastAPI()


@app.post(src.consts.WEBHOOK_URL_PATH)
async def process_webhook(update: dict):
    """
    Process webhook calls
    """
    if update:
        update = Update.de_json(update)
        await bot.process_new_updates([update])
    else:
        return


@app.get("/", status_code=201)
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
    await bot.send_photo(
        message.chat.id,
        src.consts.START_IMAGE,
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
        "найдёшь тут: https://t.me/sneaky_dice",
    )


@bot.message_handler(commands=["help", "about"], chat_types=["private"])
async def handle_about(
    message: Message, session: AsyncSession, user: User, state: StateContext
):
    await state.delete()
    await bot.send_message(
        message.chat.id,
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
        f"• Бусти - {src.consts.BOOSTY_LINK}\n"
        f"• Крипта - USDT (TRC20 | TRON) {src.consts.CRYPTO_LINK} \n\n"
        f"Больше полезных материалов к ролевым играм ты найдёшь "
        f"тут: https://t.me/sneaky_dice",
    )


@bot.message_handler(commands=["search"], chat_types=["private"])
async def find_game(
    message: Message, session: AsyncSession, user: User, state: StateContext
):
    await state.delete()
    invite_link = (
        await bot.export_chat_invite_link(src.consts.NEWS_CHANNEL_ID)
        if src.consts.ENVIRONMENT == "local"
        else "https://t.me/SneakyDiceGames"
    )
    if user.registered:
        text = (
            "Все активные игры ты можешь увидеть в канале "
            "https://t.me/SneakyDiceGames. Если что-то понравится, "
            "то нажми там на кнопку “Подать заявку”."
        )
    else:
        text = (
            "Все активные игры ты можешь увидеть в канале "
            "https://t.me/SneakyDiceGames. Но у тебя не получится откликнуться, "
            "пока ты не зарегистрирован. Чтобы зарегистрироваться выбери в меню "
            "слева внизу команду “Регистрация” или отправь команду /register."
        )
    await send_message_with_link_button(
        bot,
        message.chat.id,
        text,
        "Канал с играми",
        invite_link,
        photo=src.consts.SEARCH_IMAGE,
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
            allowed_updates=src.consts.ALLOWED_UPDATE_TYPES, logger_level=logging.INFO
        )
    )
