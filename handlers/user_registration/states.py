from telebot.states import StatesGroup, State


class RegistrationStates(StatesGroup):
    name = State()
    age = State()
    city = State()
    timezone = State()
    user_type = State()
    bio = State()