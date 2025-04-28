from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import ADMIN_IDS
from handlers.administration.settings import (
    SendNotificationStates,
    NotificationTypeEnum,
    SEND_NOTIFICATION_CALLBACK_PREFIX,
)
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler
from utils.message_helpers import create_markup


class SendNotificationHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["send_notification"],
            func=(lambda message: message.chat.id in ADMIN_IDS),
            chat_types=["private"],
        )

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        keyboard = create_markup(
            (
                ("Платным ДМам", NotificationTypeEnum.to_paid_dms.value),
                ("Бесплатным ДМам", NotificationTypeEnum.to_free_dms.value),
                ("Игрокам", NotificationTypeEnum.to_players.value),
                ("Всем", NotificationTypeEnum.to_all.value),
                ("Кастомный фильтр", NotificationTypeEnum.custom_filter.value),
            ),
            SEND_NOTIFICATION_CALLBACK_PREFIX,
        )

        await self.bot.send_message(
            message.chat.id,
            "Выбери, кому отправить уведомления.",
            reply_markup=keyboard,
        )
        await state.set(SendNotificationStates.choose_type)
