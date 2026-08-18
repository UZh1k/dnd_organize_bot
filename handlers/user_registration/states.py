from telebot.states import State, StatesGroup


class UserRegistrationStates(StatesGroup):
    name = State()
    age = State()
    accept_minor = State()
    city = State()
    timezone = State()
    user_type = State()
    bio = State()
