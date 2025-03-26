import locale

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from consts import BOT_USERNAME
from models import (
    Game,
    User,
    UserTypeText,
    UserType,
    ReviewStatistic,
    Review,
    ReviewReceiverTypeEnum,
)
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


def create_markup(
    items: tuple[tuple[str, str], ...],
    form_item_name: str,
    row_width: int = 1,
    form_prefix: str | None = None,
):
    markup = InlineKeyboardMarkup()
    prefix = f"{form_prefix}:{form_item_name}" if form_prefix else form_item_name

    markup.add(
        *(
            InlineKeyboardButton(name, callback_data=f"{prefix}:{data}")
            for name, data in items
        ),
        row_width=row_width,
    )
    return markup


def review_statistic_text(statistic: ReviewStatistic, with_comments_count: bool = True):
    if not statistic.total_count:
        return "0 отзывов"

    s = f"{statistic.rating:.1f}⭐️, всего отзывов - {statistic.total_count}"
    if with_comments_count:
        s += f", с комментариями - {statistic.comments_count}"
    return s


def generate_review_text(review: Review, review_index: int, total_count: int):
    comment_text = f"Комментарий: {review.comment}\n" if review.comment else ""
    locale.setlocale(locale.LC_ALL, "")
    return (
        f"Отзыв {'мастеру' if review.receiver_type == ReviewReceiverTypeEnum.dm else 'игроку'} "
        f"{review.to_user.name} "
        f"{review_index + 1}/{total_count}\n\n"
        f"Пользователь: {review.from_user.name}\n"
        f"Оценка: {review.value}⭐️\n"
        f"{comment_text}\n"
        f"Дата: {review.created:%d %B, %Y, %H:%M}\n"
    )
