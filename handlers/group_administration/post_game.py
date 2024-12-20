from datetime import datetime

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.types import Message

from consts import NEWS_CHANNEL_ID
from controllers.game import GameController
from models import Game, User
from utils.game_text import create_game_text, create_game_markup


async def create_game_post(bot: AsyncTeleBot, game: Game, update_text: str = ""):
    post_message = await bot.send_photo(
        NEWS_CHANNEL_ID,
        game.image,
        create_game_text(game, update_text),
        reply_markup=create_game_markup(game),
        parse_mode="Markdown",
    )
    game.post_id = post_message.id
    game.last_update = datetime.now()


async def update_game_post(
    message: Message, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    chat_member = await bot.get_chat_member(message.chat.id, user.id)
    if chat_member.status not in ["administrator", "creator"]:
        return

    game = await GameController.get_one(message.chat.id, session, "group_id")
    if not game or not game.active:
        await bot.send_message(message.chat.id, "Игра еще не привязана или уже закрыта")
        return
    if game.last_update and game.last_update + timedelta(minutes=10) > datetime.now():
        await bot.send_message(
            message.chat.id,
            "Публикацию можно поднимать не чаще, чем раз в 10 минут. Попробуй позже.",
        )
        return
    try:
        await bot.edit_message_caption(
            f"*{game.title}*\n\n" "Пост пересоздан",
            NEWS_CHANNEL_ID,
            game.post_id,
            parse_mode="Markdown",
        )
        await create_game_post(bot, game, update_text=f"Идет донабор на игру!\n\n")
        await bot.send_message(
            message.chat.id,
            "Я обновил твою публикацию. Постараюсь побыстрее найти игроков.",
        )
    except ApiTelegramException:
        pass
