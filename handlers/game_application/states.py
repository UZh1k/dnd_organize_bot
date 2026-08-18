from telebot.states import State, StatesGroup


class GameApplicationStates(StatesGroup):
    choice = State()
    letter = State()
