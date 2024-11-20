from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from controllers.game import GameController
from controllers.game_application import GameApplicationController
from handlers.game_application.states import GameApplicationStates
from models import User
from utils.message_helpers import send_message_with_link_button


GAME_APPLICATION_NO_DATA = "GameApplication:no_data"


async def handle_apply_for_game(
    message: Message,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    game_id = int(message.text.split()[-1])
    game = await GameController.get_one(game_id, session)
    if not game or not game.active:
        await bot.send_message(message.chat.id, "TBD Игра уже неактивна")
        return
    game_application = await GameApplicationController.get_one(
        game_id, user.id, session
    )
    if game_application:
        await bot.send_message(message.chat.id, "TBD Ты уже подавал заявку на эту игру")
        return
    if not user.registered:
        await send_message_with_link_button(
            bot,
            message.chat.id,
            "TBD Ты еще не зарегистрировался /register",
            "TBD Податься на игру",
        )
        return
    await state.set(GameApplicationStates.letter)
    await state.add_data(game_id=game_id)
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "TBD Податься без письма", callback_data=GAME_APPLICATION_NO_DATA
        )
    )
    await bot.send_message(
        message.chat.id, f"TBD Напиши сопроводительное письмо", reply_markup=markup
    )
