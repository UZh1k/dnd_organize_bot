from telebot.states import StatesGroup, State


class SendNotificationStates(StatesGroup):
    handle_text = State()
