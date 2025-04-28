from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.administration.settings import SEND_NOTIFICATION_CALLBACK_PREFIX, \
    SendNotificationStates, NotificationTypeEnum
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler


class NotificationTypeHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data.startswith(SEND_NOTIFICATION_CALLBACK_PREFIX),
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        notification_type = call.data.split(":")[-1]

        if notification_type == NotificationTypeEnum.custom_filter.value:
            await self.bot.send_message(
                call.message.chat.id,
                "Напиши кастомный фильтр"
            )
            await state.set(SendNotificationStates.custom_filter)
        else:
            await self.bot.send_message(
                call.message.chat.id,
                "Напиши сообщение, которое отправится всем, "
                "кого ты выбрал (без дупликатов)"
            )
            await state.set(SendNotificationStates.handle_text)

        await state.add_data(notification_type=notification_type)
