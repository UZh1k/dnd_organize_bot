from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from consts import BOT_USERNAME
from models import Game


async def send_message_with_link_button(
    bot: AsyncTeleBot,
    chat_id: int,
    text: str,
    button_text: str,
    button_url: str,
    photo: str | None = None,
):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(button_text, url=button_url))
    if photo:
        await bot.send_photo(chat_id, photo, text, reply_markup=markup)
    else:
        await bot.send_message(chat_id, text, reply_markup=markup)


def generate_link_for_game_apply(game: Game):
    return f"https://t.me/{BOT_USERNAME}?start={game.id}"
