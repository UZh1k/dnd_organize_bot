from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


async def send_message_with_link_button(
    bot: AsyncTeleBot, chat_id: int, text: str, button_text: str, button_url: str
):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(button_text, url=button_url))
    await bot.send_message(chat_id, text, reply_markup=markup)
