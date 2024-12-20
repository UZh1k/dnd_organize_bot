from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from models import Game, GameFormatText, GameFormat, GameType, GameTypeText
from utils.message_helpers import generate_link_for_game_apply
from utils.other import (
    POPULAR_CITIES,
    create_tag,
    POPULAR_SYSTEMS,
    POPULAR_DND_SETTINGS,
    POPULAR_DND_REDACTIONS,
)


def create_game_text(game: Game, update_text: str = "", players_count: int = 0) -> str:
    city_text = f"Город: {game.city.name}\n" if game.city else ""

    players_at_all = (
        f"{game.min_players}"
        if game.min_players == game.max_players
        else f"{game.min_players}-{game.max_players}"
    )

    players_count_left = f", уже в группе {players_count}" if players_count else ""

    players_age = (
        f"{game.min_age}-{game.max_age}" if game.max_age else f"{game.min_age}+"
    )
    about_price = f" - {game.about_price}" if game.about_price else ""

    city_tag = (
        f"#{create_tag(game.city.name)} "
        if game.city and game.city.name in POPULAR_CITIES
        else ""
    )
    system_tag = (
        f"#{create_tag(game.system)} " if game.system in POPULAR_SYSTEMS else ""
    )
    setting_tag = (
        f"#{create_tag(game.setting)} " if game.setting in POPULAR_DND_SETTINGS else ""
    )
    redaction_tag = (
        f"#{create_tag(game.redaction)} "
        if game.redaction in POPULAR_DND_REDACTIONS
        else ""
    )
    free_status = "Платно" if not game.free else "Бесплатно"

    format_name = GameFormatText[GameFormat(game.format).name].value
    type_name = GameTypeText[GameType(game.type).name].value
    return (
        f"*{game.title}*\n\n"
        f"{update_text}"
        f"Формат: {format_name}\n"
        f"{city_text}"
        f"Количество игроков: всего {players_at_all}{players_count_left}\n"
        f"Цена: {free_status}{about_price}\n"
        f"Время проведения: {game.time}\n\n"
        f"Игровая система: {game.system}\n"
        f"Редакция и сеттинг: {game.redaction} "
        f"{f', {game.setting}' if game.setting != game.redaction else ''}\n"
        f"Тип игры:  {type_name}\n"
        f"Уровень игроков на старте: {game.start_level}\n\n"
        f"Описание: {game.description}\n\n"
        f"Требование к возрасту: {players_age}\n"
        f"Требование к игрокам: {game.tech_requirements}\n\n"
        f"#{format_name} {city_tag}"
        f"#{free_status} {system_tag}{setting_tag}{redaction_tag}#{type_name} "
        f"{' '.join(f'#{tag.title}' for tag in game.tags)}\n"
    )


def create_game_markup(game: Game):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Подать заявку", url=generate_link_for_game_apply(game))
    )
    return markup
