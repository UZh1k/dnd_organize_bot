from enum import Enum
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from controllers.game import GameController
from controllers.game_application import GameApplicationController
from models import User

ACCEPT_FORM_CALLBACK_PREFIX = "AcceptForm"


class ApplyAnswer(Enum):
    yes = "yes"
    no = "no"


def generate_accept_callback(game_id: int, user_id: int, answer: Literal["yes", "no"]):
    return f"{ACCEPT_FORM_CALLBACK_PREFIX}:{game_id}:{user_id}:{answer}"


def get_data_from_accept_callback(callback_data: str) -> tuple[int, int]:
    _, game_id, user_id, _ = callback_data.split(":")
    return int(game_id), int(user_id)


def generate_accept_form_markup(game_id: int, user_id: int):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(
            "✔️", callback_data=generate_accept_callback(game_id, user_id, "yes")
        ),
        InlineKeyboardButton(
            "✖️", callback_data=generate_accept_callback(game_id, user_id, "no")
        ),
    )
    return markup


async def handle_decline_application(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    game_id, user_id = get_data_from_accept_callback(call.data)
    game = await GameController.get_one(game_id, session)
    await GameApplicationController.set_status(game_id, user_id, False, session)
    await bot.send_message(user_id, f"TBD Заявка на игру {game.title} отклонена")
    await bot.answer_callback_query(callback_query_id=call.id, text="Заявка отклонена")
    await bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id, reply_markup=None
    )


async def handle_accept_application(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    game_id, user_id = get_data_from_accept_callback(call.data)
    game = await GameController.get_one(game_id, session)
    await GameApplicationController.set_status(game_id, user_id, True, session)
    await bot.send_message(user_id, f"TBD Заявка на игру {game.title} принята")
    await bot.answer_callback_query(callback_query_id=call.id, text="Заявка принята")
    await bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id, reply_markup=None
    )
