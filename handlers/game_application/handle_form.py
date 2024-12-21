from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery, Message

from controllers.game import GameController
from controllers.game_application import GameApplicationController
from handlers.game_application.states import GameApplicationStates
from handlers.game_application.accept_form import generate_accept_form_markup
from models import User
from utils.message_helpers import get_user_text


async def send_application(
    bot: AsyncTeleBot,
    user: User,
    session: AsyncSession,
    game_id: int,
    form_text: str | None = None,
):
    game = await GameController.get_one(game_id, session)
    if not game or not game.active:
        await bot.send_message(user.id, "Игра закрыта или не существует")
        return
    await GameApplicationController.create(game_id, user.id, session)
    await bot.send_message(user.id, "Заявка отправлена")

    await bot.send_message(
        game.creator_id,
        f"Я нашел тебе игрока для приключения “{game.title}”. "
        f"Жду твоего одобрения, чтобы пригласить его в группу.\n\n"
        f"{get_user_text(user)}\n\n"
        f"{form_text if form_text else ''}",
        reply_markup=generate_accept_form_markup(game_id, user.id),
    )


async def handle_application_letter_no_data(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    try:
        await bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=None
        )
        if await state.get() == GameApplicationStates.letter.name:
            async with state.data() as data:
                await send_application(bot, user, session, data["game_id"])
            await state.delete()
    except ApiTelegramException:
        pass


async def handle_application_cancel(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    try:
        await bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=None
        )
        if await state.get() == GameApplicationStates.letter.name:
            await state.delete()
            await bot.send_message(
                call.message.chat.id,
                "Ты отменил заявку на игру. Давай поищем другие игры в канале - "
                "https://t.me/SneakyDiceGames",
            )
    except ApiTelegramException:
        pass


async def handle_application_letter(
    message: Message,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    async with state.data() as data:
        await send_application(
            bot, user, session, data["game_id"], form_text=message.text
        )
    await state.delete()
