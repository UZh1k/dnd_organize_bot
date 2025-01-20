from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.types import Update, User

from src.consts import NEWS_CHANNEL_ID
from src.controllers.game import GameController
from src.controllers.game_member import GameMemberController
from src.controllers.user import UserController
from src.handlers.group_administration.group_funcs import on_close_game
from src.models import Game
from src.utils.game_text import create_game_text, create_game_markup


async def on_players_count_change(game: Game, bot: AsyncTeleBot, players_count: int):
    try:
        if game.active:
            await bot.edit_message_caption(
                create_game_text(game, players_count=players_count),
                NEWS_CHANNEL_ID,
                game.post_id,
                parse_mode="Markdown",
                reply_markup=create_game_markup(game),
            )
    except ApiTelegramException:
        pass


async def handle_player_added_to_group(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    user_id = update.new_chat_member.user.id
    if not await UserController.get_one(user_id, session):
        new_user = update.new_chat_member.user
        await UserController.create(
            {"id": user_id, "username": new_user.username}, session
        )
    game = await GameController.get_one(update.chat.id, session, "group_id")
    if not game:
        await bot.send_message(
            update.chat.id,
            "Чтобы я отслеживал количество игроков, привяжи к "
            "группе игру с помощью команды /link.",
        )
        return
    try:
        await GameMemberController.create(
            {"game_id": game.id, "user_id": user_id}, session
        )
    except SQLAlchemyError:
        pass
    players_count = await GameMemberController.count_game_members(game.id, session)
    if game.max_players <= players_count:
        await bot.send_message(
            update.chat.id,
            "Похоже, что необходимое количество участников уже набралось. "
            "Используй команду /done, чтобы закончить поиск игроков, "
            "или команду /update, чтобы поднять игру в поиске.",
        )
    elif game.min_players <= players_count:
        await bot.send_message(
            update.chat.id,
            "Минимальное количество участников уже набралось. "
            "Используй команду /done, чтобы закончить поиск игроков, "
            "команду /update, чтобы поднять игру в поиске, "
            "или /close, чтобы отменить игру.",
        )
    await on_players_count_change(game, bot, players_count)


async def handle_player_left_group(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    user_id = update.new_chat_member.user.id
    if not await UserController.get_one(user_id, session):
        new_user = update.new_chat_member.user
        await UserController.create(
            {"id": user_id, "username": new_user.username}, session
        )
    game = await GameController.get_one(update.chat.id, session, "group_id")
    if not game:
        return
    if game.creator_id == user_id:
        if not game.done:
            await on_close_game(bot, game, session)
    else:
        await GameMemberController.delete_game_member(game.id, user_id, session)
    players_count = await GameMemberController.count_game_members(game.id, session)
    await on_players_count_change(game, bot, players_count)
