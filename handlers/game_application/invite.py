import traceback

from telebot.asyncio_helper import ApiTelegramException
from telebot.async_telebot import AsyncTeleBot

from consts import EXCEPTION_CHAT_ID
from models import Game
from utils.message_helpers import send_message_with_link_button


async def send_invite(user_id: int, bot: AsyncTeleBot, game: Game):
    try:
        invite_link = await bot.create_chat_invite_link(game.group_id)
        await send_message_with_link_button(
            bot,
            user_id,
            f"Мастер игры уже ждет тебя на приключение “{game.title}”! "
            f"Добавляйся в группу. Нажми на кнопку ниже. "
            f"Если ссылка неактивна, попробуй заново подать заявку на игру",
            "Присоединитья к игре",
            invite_link.invite_link,
        )
    except ApiTelegramException:
        await bot.send_message(
            user_id, "Возникла некоторая проблема, я ее уже передал своим создателям"
        )
        await bot.send_message(
            EXCEPTION_CHAT_ID,
            f"❗️ Пользователь не может зайти в игру\n"
            f"user_id: {user_id}\n"
            f"game_id: {game.id}",
        )
        print(traceback.print_exc())
        pass
