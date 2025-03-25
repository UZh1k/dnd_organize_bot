from telebot.states import StatesGroup, State


class GameApplicationStates(StatesGroup):
    choice = State()
    letter = State()
