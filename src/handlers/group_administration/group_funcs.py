from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.types import Update, Message

from src.consts import NEWS_CHANNEL_ID, BOOSTY_LINK, CRYPTO_LINK
from src.controllers.game import GameController
from src.models import User, Game


async def handle_bot_added_to_group(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    await bot.send_message(
        update.chat.id,
        "Спасибо, что добавил меня. Чтобы я мог работать без ошибок, нужно "
        "открыть историю чата. Для этого зайди в настройки группы и поменяй "
        "“Историю чата” на “Видна”.\n\n"
        "Если вкратце, это самый простой способ, как сделать из группы супергруппу, "
        "чтобы при работе с ней не возникало никаких проблем. "
        "Ты сможешь потом поменять эту настройку в любой момент.",
    )

async def handle_bot_added_to_supergroup(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    await bot.send_message(
        update.chat.id,
        "Супер! Чтобы я мог работать корректно, мне нужно получить права "
        "администратора. Зайди в список участников. Сделай долгое нажатие на моем "
        "имени и появится кнопка “Сделать админом”. Нажми на нее и поставь везде "
        "галочки. Если ты с ПК, то зайди в настройки группы, в раздел администраторы "
        "и добавь меня там.",
    )


async def on_close_game(bot: AsyncTeleBot, game: Game, session: AsyncSession):
    game.active = False
    game.done = False
    await session.flush()
    try:
        await bot.edit_message_caption(
            f"*{game.title}*\n\n" f"Сбор на приключение прекращен.",
            NEWS_CHANNEL_ID,
            game.post_id,
            reply_markup=None,
            parse_mode="Markdown",
        )
    except ApiTelegramException:
        pass


async def handle_bot_removed_group(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    game = await GameController.get_one(update.chat.id, session, "group_id")
    if game:
        game.group_id = None

        if not game.done:
            await on_close_game(bot, game, session)


async def close_game(
    message: Message, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    chat_member = await bot.get_chat_member(message.chat.id, user.id)
    if chat_member.status not in ["administrator", "creator"]:
        await bot.send_message(
            message.chat.id,
            "Только администратор или создатель игры иожет ее закрыть",
        )
        return
    game = await GameController.get_one(message.chat.id, session, "group_id")
    if not game or not game.active:
        await bot.send_message(
            message.chat.id, "Игра еще не привязана или уже неактивна"
        )
        return
    await on_close_game(bot, game, session)
    await bot.send_message(
        message.chat.id,
        "Жаль, что не удалось набрать команду. "
        "Ты всегда можешь создать новую публикацию, "
        "написав мне в личные сообщения. Надеюсь, что скоро увидимся.",
    )


async def done_game(
    message: Message, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    chat_member = await bot.get_chat_member(message.chat.id, user.id)
    if chat_member.status not in ["administrator", "creator"]:
        await bot.send_message(
            message.chat.id,
            "Только администратор или создатель игры иожет ее закрыть",
        )
        return
    game = await GameController.get_one(message.chat.id, session, "group_id")
    if not game or not game.active:
        await bot.send_message(message.chat.id, "Игра еще не привязана уже неактивна")
        return
    game.active = False
    game.done = True
    try:
        await bot.edit_message_caption(
            f"*{game.title}*\n\n" f"Команда собралась и отправилась в приключение!",
            NEWS_CHANNEL_ID,
            game.post_id,
            reply_markup=None,
            parse_mode="Markdown",
        )
    except ApiTelegramException:
        pass
    await bot.send_message(
        message.chat.id,
        "Поздравляю! Желаю всем приятной игры. Закрываю набор игроков.\n\n"
        "Если вам понравилась моя работа, то буду очень благодарен любым донатам. "
        "Денежные средства пойдут в первую очередь на оплату хостинга и серверов, "
        "а во вторую на развитие нового функционала. Спасибо!\n\n"
        f"• Бусти - {BOOSTY_LINK} \n"
        f"• Крипта - USDT (TRC20 | TRON) {CRYPTO_LINK}",
    )
