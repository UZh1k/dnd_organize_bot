from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from consts import BOT_USERNAME
from models import Game, User, UserTypeText, UserType
from utils.other import utc_to_relative_msk


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


def get_chunks(s, maxlength):
    start = 0
    end = 0
    while start + maxlength < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end + 1
    yield s[start:]


def get_user_text(user: User):
    user_role = UserTypeText[UserType(user.user_type).name].value
    return (
        f"Имя: {user.name}\n"
        f"Возраст: {user.age}\n"
        f"Город: {user.city.name}\n"
        f"Часовой пояс: {utc_to_relative_msk(user.timezone)} ({user.timezone})\n"
        f"Роль в НРИ: {user_role}\n"
        f"Об игроке: {user.bio}"
    )
