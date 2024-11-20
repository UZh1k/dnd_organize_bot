from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup

from controllers.game import GameController
from controllers.game_application import GameApplicationController
from handlers.game_application.accept_form import generate_accept_form_markup
from models import User


async def send_application(
    bot: AsyncTeleBot,
    user: User,
    session: AsyncSession,
    game_id: int,
    form_text: str | None = None,
):
    game = await GameController.get_one(game_id, session)
    if not game or not game.active:
        await bot.send_message(user.id, "TBD Игра закрыта или не существует")
        return
    await GameApplicationController.create(game_id, user.id, session)
    await bot.send_message(user.id, "TBD Заявка отправлена")
    await bot.send_message(
        game.creator_id,
        f"TBD Заявка от игрока {user.name} {form_text}",
        reply_markup=generate_accept_form_markup(game_id, user.id),
    )


async def handle_application_letter_no_data(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    async with state.data() as data:
        await send_application(bot, user, session, data["game_id"])
    await state.delete()
    await bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id, reply_markup=None
    )


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
