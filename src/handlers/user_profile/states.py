from telebot.states import StatesGroup, State


class UserProfileStates(StatesGroup):
    name = State()
    age = State()
    accept_minor = State()
    city = State()
    timezone = State()
    user_type = State()
    bio = State()