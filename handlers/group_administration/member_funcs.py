from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Update, User

from controllers.game import GameController
from controllers.game_member import GameMemberController


async def handle_player_added_to_group(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    user_id = update.new_chat_member.user.id
    game = await GameController.get_one(update.chat.id, session, "group_id")
    await GameMemberController.create(game.id, user_id, session)
    if game.max_players <= await GameMemberController.count_game_members(
        game.id, session
    ):
        await bot.send_message(
            update.chat.id,
            "Похоже, что необходимое количество участников уже набралось. "
            "Используй команду /done, чтобы закончить поиск игроков, "
            "или команду /update, чтобы опустить игру в поиске.",
        )
    elif game.min_players <= await GameMemberController.count_game_members(
        game.id, session
    ):
        await bot.send_message(
            update.chat.id,
            "Минимальное количество участников уже набралось. "
            "Используй команду /done, чтобы закончить поиск игроков, "
            "команду /update, чтобы опустить игру в поиске, "
            "или /close, чтобы отменить игру.",
        )


async def handle_player_left_group(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    user_id = update.new_chat_member.user.id
    game = await GameController.get_one(update.chat.id, session, "group_id")
    await GameMemberController.delete_game_member(game.id, user_id, session)
