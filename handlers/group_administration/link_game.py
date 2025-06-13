from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
    Message,
    CallbackQuery,
)

from controllers.game import GameController
from handlers.group_administration.post_game import create_game_post
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
            "Создай игру через чат с ботом и нажми /link, чтобы привязать игру",
        )
    else:
        await bot.send_message(
            chat_id,
            "Отлично. Теперь можем опубликовать твою игру. "
            "Смотри, что мне удалось найти. Выбери нужную игру.",
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
    if update.chat.type == "group":
        await bot.send_message(
            update.chat.id,
            "Чтобы я мог работать без ошибок, нужно "
            "открыть историю чата. Для этого зайди в настройки группы и поменяй "
            "“Историю чата” на “Видна”.\n\n"
            "Если вкратце, это самый простой способ, как сделать из "
            "группы супергруппу, "
            "чтобы при работе с ней не возникало никаких проблем. "
            "Ты сможешь потом поменять эту настройку в любой момент.",
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
    if message.chat.type == "group":
        await bot.send_message(
            message.chat.id,
            "Чтобы я мог работать без ошибок, нужно "
            "открыть историю чата. Для этого зайди в настройки группы и поменяй "
            "“Историю чата” на “Видна”.\n\n"
            "Если вкратце, это самый простой способ, как сделать из "
            "группы супергруппу, "
            "чтобы при работе с ней не возникало никаких проблем. "
            "Ты сможешь потом поменять эту настройку в любой момент.",
        )
        return
    await send_link_game(message.chat.id, bot, session, user)


async def handle_link_game(
    call: CallbackQuery, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    try:
        await bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=None
        )
    except ApiTelegramException:
        return
    if await GameController.get_one(call.message.chat.id, session, "group_id"):
        await bot.send_message(call.message.chat.id, "Группа уже привязана к игре")
        return
    game_id = int(call.data.split(":")[-1])
    game = await GameController.get_one(game_id, session)
    game.group_id = call.message.chat.id
    game.first_post_datetime = datetime.now()
    await bot.answer_callback_query(callback_query_id=call.id, text="Группа привязана")

    await create_game_post(bot, game, session)

    await bot.send_message(
        call.message.chat.id,
        "Отлично. Я опубликовал твою игру в "
        "[канале](https://t.me/SneakyDiceGames). "
        "Как только кто-то из игроков откликнется, "
        "я пришлю тебе личное сообщение с анкетой.\n\n"
        "Если игроки не наберутся за нужное время, то ты можешь поднять "
        "публикацию в списке, отправив мне сюда команду /update. "
        "Когда ты наберешь полную группу, то пришли, пожалуйста сюда команду "
        "/done. Если передумаешь проводить игру, то пришли такую же команду "
        "- /close. \n\n"
        "Недавно мы добавили новую возможность - теперь можно возобновлять поиск "
        "уже собранной игры командой /update, обязательно попробуй!",
        parse_mode="Markdown",
    )