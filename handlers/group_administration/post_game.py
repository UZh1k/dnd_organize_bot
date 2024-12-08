from datetime import datetime

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from consts import BOT_USERNAME, NEWS_CHANNEL_ID
from controllers.game import GameController
from models import Game, User, GameFormatText, GameTypeText, GameFormat, GameType
from utils.message_helpers import generate_link_for_game_apply
from utils.other import POPULAR_CITIES, POPULAR_SYSTEMS


async def create_game_post(bot: AsyncTeleBot, game: Game, for_update: bool = False):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Подать заявку", url=generate_link_for_game_apply(game))
    )
    city_text = f"Город: {game.city.name}\n" if game.city else ""
    players_count = (
        f"{game.min_players}"
        if game.min_players == game.max_players
        else f"{game.min_players}-{game.max_players}"
    )
    players_age = (
        f"{game.min_age}"
        if game.min_age == game.max_age
        else f"{game.min_age}-{game.max_age}"
    )
    about_price = f" - {game.about_price}" if game.about_price else ""

    city_tag = f"#{game.city.name} " if game.city in POPULAR_CITIES else ""
    system_tag = f"#{game.system} " if game.system in POPULAR_SYSTEMS else ""
    free_status = "Платно" if not game.free else "Бесплатно"

    update_text = f"Идет донабор на игру!\n\n" if for_update else ""

    format_name = GameFormatText[GameFormat(game.format).name].value
    type_name = GameTypeText[GameType(game.type).name].value

    post_message = await bot.send_photo(
        NEWS_CHANNEL_ID,
        game.image,
        f"*{game.title}*\n\n"
        f"{update_text}"
        f"Формат: {format_name}\n"
        f"{city_text}"
        f"Количество игроков: {players_count}\n"
        f"Платность: {free_status}{about_price}\n"
        f"Время проведения: {game.time}\n\n"
        f"Игровая система: {game.system}\n"
        f"Тип игры:  {type_name}\n\n"
        f"Описание: {game.description}\n\n"
        f"Требование к возрасту: {players_age}\n"
        f"Требование к игрокам: {game.tech_requirements}\n\n"
        f"#{format_name} {city_tag}"
        f"#{free_status} {system_tag}#{type_name}",
        reply_markup=markup,
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
        await bot.send_message(message.chat.id, "TBD Игра уже закрыта")
        return
    if game.last_update and game.last_update + timedelta(days=7) > datetime.now():
        await bot.send_message(
            message.chat.id,
            "Публикацию можно поднимать не чаще, чем раз в неделю. Попробуй позже.",
        )
        return
    try:
        await bot.edit_message_caption(
            f"*{game.title}*\n\n"
            "Пост пересоздан",
            NEWS_CHANNEL_ID,
            game.post_id,
            parse_mode="Markdown",
        )
        await create_game_post(bot, game, for_update=True)
        await bot.send_message(
            message.chat.id,
            "Я обновил твою публикацию. Постараюсь побыстрее найти игроков.",
        )
    except Exception as e:
        print(str(e))
