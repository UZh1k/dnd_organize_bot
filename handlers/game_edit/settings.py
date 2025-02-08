from enum import Enum
from typing import Final

from telebot.states import State, StatesGroup

GAME_EDIT_FORM_PREFIX: Final[str] = "GameEdit"
GameEditState = State()


class GameEditCallbackPrefixes(Enum):
    choose_game = "choose_game"
    game_action = "game_action"
    choose_option = "choose_option"


class GameEditActions(Enum):
    edit = "edit"
    delete = "delete"
    delete_confirm = "delete_confirm"
    skip = "skip"
    cancel = "cancel"


class GameEditOptions(Enum):
    title = "title"
    format = "format"
    city = "city"
    players_count = "players_count"
    free = "free"
    time = "time"
    system = "system"
    dnd_redaction = "dnd_redaction"
    dnd_setting = "dnd_setting"
    redaction_and_setting = "redaction_and_setting"
    setting = "setting"
    type = "type"
    start_level = "start_level"
    description = "description"
    players_age = "players_age"
    tech_requirements = "tech_requirements"
    image = "image"
    tag = "tag"


class GameEditOptionsStr(Enum):
    title = "Название игры"
    format = "Формат"
    city = "Город"
    players_count = "Количество игроков"
    free = "Цена"
    time = "Время проведения"
    system = "Игровая система"
    dnd_redaction = "Редакция"
    dnd_setting = "Сеттинг"
    redaction_and_setting = "Редакция и сеттинг"
    type = "Тип игры"
    start_level = "Уровень игроков"
    description = "Описание игры"
    players_age = "Требование к возрасту"
    tech_requirements = "Требование к игрокам"
    image = "Картинка"
    tag = "Теги"


class GameEditStates(StatesGroup):
    title = State()
    format = State()
    accept_offline = State()
    accept_city = State()
    city = State()
    system = State()
    dnd_redaction = State()
    dnd_setting = State()
    redaction_and_setting = State()
    type = State()
    description = State()
    start_level = State()
    players_count = State()
    free = State()
    about_price = State()
    time = State()
    players_age = State()
    tech_requirements = State()
    image = State()
    tag = State()
