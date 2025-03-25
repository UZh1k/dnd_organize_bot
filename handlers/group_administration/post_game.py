from datetime import datetime

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.types import Message

from consts import NEWS_CHANNEL_ID
from controllers.game import GameController
from controllers.game_member import GameMemberController
from models import Game, User
from utils.game_text import create_game_text, create_game_markup


async def create_game_post(
    bot: AsyncTeleBot,
    game: Game,
    session: AsyncSession,
    update_text: str = "",
    players_count: int = 0,
):
    post_message = await bot.send_photo(
        NEWS_CHANNEL_ID,
        game.image,
        create_game_text(game, update_text, players_count),
        reply_markup=await create_game_markup(game, session),
        parse_mode="Markdown",
    )
    game.post_id = post_message.id
    game.last_update = datetime.now()


async def update_game_post(
    message: Message, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    update_days_delta = timedelta(days=5)

    chat_member = await bot.get_chat_member(message.chat.id, user.id)
    if chat_member.status not in ["administrator", "creator"]:
        return

    game = await GameController.get_one(message.chat.id, session, "group_id")
    if not game or (not game.active and not game.done):
        await bot.send_message(message.chat.id, "Игра еще не привязана или уже закрыта")
        return

    if (
        not game.done
        and game.last_update
        and game.last_update + update_days_delta > datetime.now()
    ):
        await bot.send_message(
            message.chat.id,
            "Публикацию можно поднимать не чаще, чем раз в 5 дней. Попробуй позже.",
        )
        return

    try:
        players_count = await GameMemberController.count_game_members(game.id, session)

        if game.done:
            game.done = None
            game.active = True
            if (
                game.last_update
                and game.last_update + update_days_delta > datetime.now()
            ):
                try:
                    await bot.edit_message_caption(
                        create_game_text(game, players_count=players_count),
                        NEWS_CHANNEL_ID,
                        game.post_id,
                        parse_mode="Markdown",
                        reply_markup=await create_game_markup(game, session),
                    )
                except ApiTelegramException:
                    await create_game_post(
                        bot,
                        game,
                        session,
                        update_text=f"Донабор!\n\n",
                        players_count=players_count,
                    )

                game.active = True
                await bot.send_message(
                    message.chat.id,
                    "Я обновил твою публикацию. Постараюсь побыстрее найти игроков.",
                )
                return

        try:
            await bot.edit_message_caption(
                f"*{game.title}*\n\n" "Пост пересоздан",
                NEWS_CHANNEL_ID,
                game.post_id,
                parse_mode="Markdown",
            )
        except ApiTelegramException:
            pass

        await create_game_post(
            bot, game, session, update_text=f"Донабор!\n\n", players_count=players_count
        )
        await bot.send_message(
            message.chat.id,
            "Я обновил твою публикацию. Постараюсь побыстрее найти игроков.",
        )

    except ApiTelegramException:
        pass
