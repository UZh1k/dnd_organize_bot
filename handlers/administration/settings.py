from enum import Enum

from telebot.states import StatesGroup, State


SEND_NOTIFICATION_CALLBACK_PREFIX = "SendNotification"


class SendNotificationStates(StatesGroup):
    choose_type = State()
    handle_text = State()


class NotificationTypeEnum(Enum):
    to_paid_dms = "to_paid_dms"
    to_free_dms = "to_free_dms"
    to_players = "to_players"
    to_all = "to_all"
