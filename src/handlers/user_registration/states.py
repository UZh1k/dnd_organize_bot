from telebot.states import StatesGroup, State


class UserRegistrationStates(StatesGroup):
    name = State()
    age = State()
    accept_minor = State()
    city = State()
    timezone = State()
    user_type = State()
    bio = State()