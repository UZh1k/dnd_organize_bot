from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException

from consts import EXCEPTION_CHAT_ID
from models import Game
from utils.message_helpers import send_message_with_link_button


async def send_invite_error_alert(
    bot: AsyncTeleBot,
    error: ApiTelegramException,
    stage: str,
    user_id: int,
    game: Game,
):
    try:
        await bot.send_message(
            EXCEPTION_CHAT_ID,
            "❗️ Не удалось отправить приглашение в игру\n"
            f"stage: {stage}\n"
            f"error: {error}\n"
            f"user_id: {user_id}\n"
            f"game_id: {game.id}\n"
            f"group_id: {game.group_id}",
        )
    except ApiTelegramException:
        pass


async def send_invite(user_id: int, bot: AsyncTeleBot, game: Game):
    try:
        chat = await bot.get_chat(game.group_id)
        invite_link = chat.invite_link
        if not invite_link:
            invite_link = await bot.export_chat_invite_link(game.group_id)
    except ApiTelegramException as error:
        try:
            await bot.send_message(
                user_id,
                "Возникла некоторая проблема, я ее уже передал своим создателям",
            )
        except ApiTelegramException:
            pass
        await send_invite_error_alert(bot, error, "create_invite_link", user_id, game)
        return

    try:
        await send_message_with_link_button(
            bot,
            user_id,
            f"Мастер игры уже ждет тебя на приключение “{game.title}”! "
            f"Добавляйся в группу. Нажми на кнопку ниже. "
            f"Если ссылка неактивна, попробуй заново подать заявку на игру",
            "Присоединитья к игре",
            invite_link,
        )
    except ApiTelegramException as error:
        await send_invite_error_alert(bot, error, "send_invite", user_id, game)
