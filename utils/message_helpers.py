import locale

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from consts import BOT_USERNAME, NEWS_CHANNEL_ID, ENVIRONMENT
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


async def get_channel_link(bot: AsyncTeleBot):
    return (
        await bot.export_chat_invite_link(NEWS_CHANNEL_ID)
        if ENVIRONMENT == "local"
        else "https://t.me/SneakyDiceGames"
    )


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


def pluralize_review(count: int) -> str:
    # forms = ["отзыв", "отзыва", "отзывов"]
    # if 11 <= count % 100 <= 14:
    #     return f"{count} {forms[2]}"
    # if count % 10 == 1:
    #     return f"{count} {forms[0]}"
    # if 2 <= count % 10 <= 4:
    #     return f"{count} {forms[1]}"
    return f"{count} отз."


def review_statistic_text(statistic: ReviewStatistic, with_comments_count: bool = True):
    if not statistic.total_count:
        return "нет отзывов"

    comments_part = ""
    if with_comments_count:
        comments_part = f", с комментарием - {statistic.comments_count}"

    return f"{statistic.rating:.1f}⭐️ ({pluralize_review(statistic.total_count)}{comments_part})"



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
