from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
    Message,
    CallbackQuery,
)

from consts import NEWS_CHANNEL_ID, BOT_USERNAME
from controllers.game import GameController
from models import Game, User

GAME_LINK_PREFIX = "GameLink"


def generate_games_markup(games: list[Game]):
    markup = InlineKeyboardMarkup()
    for game in games:
        markup.add(
            InlineKeyboardButton(
                game.title, callback_data=f"{GAME_LINK_PREFIX}:{game.id}"
            )
        )
    return markup


async def send_link_game(
    chat_id: int, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    if await GameController.get_one(chat_id, session, "group_id"):
        await bot.send_message(chat_id, "Группа уже привязана к игре")
        return
    user_games = await GameController.get_unlinked_games(user.id, session)
    if not user_games:
        await bot.send_message(
            chat_id,
            "Создай игру через бота и нажми /link, чтобы привязать игру",
        )
    else:
        await bot.send_message(
            chat_id,
            "Выбери, какую игру привязать. "
            "Если игры нет в списке, добавь ее в самом боте, "
            "а затем нажми /link здесь",
            reply_markup=generate_games_markup(user_games),
        )


async def handle_bot_promoted_to_admin(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    if not update.new_chat_member.can_invite_users:
        await bot.send_message(
            update.chat.id, "Бот должен уметь приглашать других игроков"
        )
        return
    await send_link_game(update.chat.id, bot, session, user)


async def handle_link_game_command(
    message: Message, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.status not in ["administrator", "creator"]:
        await bot.send_message(
            message.chat.id, "Только администратор может привязывать к игре группу"
        )
        return
    await send_link_game(message.chat.id, bot, session, user)


async def handle_link_game(
    call: CallbackQuery, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    game_id = int(call.data.split(":")[-1])
    game = await GameController.get_one(game_id, session)
    game.group_id = call.message.chat.id
    await bot.answer_callback_query(callback_query_id=call.id, text="Группа привязана")
    await bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id, reply_markup=None
    )
    await bot.send_message(call.message.chat.id, "Игра размещена в канале")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        "Подать заявку", url=f"https://t.me/{BOT_USERNAME}?start={game.id}"
    ))
    post_message = await bot.send_message(
        NEWS_CHANNEL_ID, f"Присоединяйтесь к игре {game.title}", reply_markup=markup
    )
    game.post_id = post_message.id
