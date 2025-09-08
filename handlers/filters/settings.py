from enum import Enum
from typing import Final

from telebot.states import State, StatesGroup

FILTERS_FORM_PREFIX: Final[str] = "Filters"


class FiltersStages(Enum):
    menu = "menu"
    search = "search"
    clear_filters = "clear_filters"
    choose_filter = "choose_filter"


class FiltersStates(StatesGroup):
    menu = State()
    age = State()
    city = State()
    platform = State()
    dnd_redaction = State()
    dnd_setting = State()
    format = State()
    free = State()
    game_type = State()
    system = State()
    tags = State()


class FilterOptions(Enum):
    age = "age"
    city = "city"
    platform = "platform"
    dnd_redaction = "dnd_redaction"
    dnd_setting = "dnd_setting"
    format = "format"
    free = "free"
    game_type = "game_type"
    system = "system"
    tags = "tags"
