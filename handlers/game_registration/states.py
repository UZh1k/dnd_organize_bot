from telebot.states import StatesGroup, State


class GameRegistrationStates(StatesGroup):
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
