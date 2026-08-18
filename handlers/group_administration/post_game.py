from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.types import Message

from consts import MAX_ACTIVE_GAMES, NEWS_CHANNEL_ID
from controllers.game import GameController
from controllers.game_member import GameMemberController
from models import Game, User
from utils.game_text import create_game_markup, create_game_text
from utils.message_helpers import is_caption_too_long_error


async def create_game_post(
    bot: AsyncTeleBot,
    game: Game,
    session: AsyncSession,
    players_count: int = 0,
):
    post_message = await bot.send_photo(
        NEWS_CHANNEL_ID,
        game.image,
        create_game_text(game, players_count),
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

    active_games_count = None
    if game.done:
        active_games_count = await GameController.get_active_games_count(
            game.creator_id, session, lock_creator=True
        )
        await session.refresh(game)

    if (
        game.done
        and active_games_count is not None
        and active_games_count >= MAX_ACTIVE_GAMES
    ):
        await bot.send_message(
            message.chat.id,
            f"У тебя уже {active_games_count} активных "
            f"наборов из {MAX_ACTIVE_GAMES} доступных. "
            f"К сожалению, не получится возобновить этот набор, "
            f"пока не закроешь один из существующих командой /close в чате сбора "
            f"или через редактирование игр командой /edit в личных сообщениях со мной.",
        )
        return

    was_done = bool(game.done)
    previous_is_update = game.is_update
    try:
        players_count = await GameMemberController.count_game_members(game.id, session)
        game.is_update = True

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
                except ApiTelegramException as error:
                    if is_caption_too_long_error(error):
                        raise
                    await create_game_post(
                        bot,
                        game,
                        session,
                        players_count=players_count,
                    )

                await bot.send_message(
                    message.chat.id,
                    "Я обновил твою публикацию. Постараюсь побыстрее найти игроков.",
                )
                return

        previous_post_id = game.post_id
        await create_game_post(bot, game, session, players_count=players_count)

        try:
            await bot.edit_message_caption(
                f"*{game.title}*\n\nПост пересоздан",
                NEWS_CHANNEL_ID,
                previous_post_id,
                parse_mode="Markdown",
            )
        except ApiTelegramException:
            pass

        await bot.send_message(
            message.chat.id,
            "Я обновил твою публикацию. Постараюсь побыстрее найти игроков.",
        )

    except ApiTelegramException as error:
        if not is_caption_too_long_error(error):
            raise
        if was_done:
            game.done = True
            game.active = False
        game.is_update = previous_is_update
        await bot.send_message(
            message.chat.id,
            "Описание игры получилось слишком длинным для публикации. "
            "Сократи его с помощью команды /edit в личных сообщениях со мной, "
            "а затем снова отправь /update.",
        )
