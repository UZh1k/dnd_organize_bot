from telebot.states import StatesGroup, State


class GameRegistrationStates(StatesGroup):
    title = State()
    format = State()
    accept_offline = State()
    city = State()
    system = State()
    type = State()
    description = State()
    players_count = State()
    free = State()
    about_price = State()
    time = State()
    players_age = State()
    tech_requirements = State()
    image = State()
