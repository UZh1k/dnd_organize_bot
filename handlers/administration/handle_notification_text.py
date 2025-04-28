import asyncio
from itertools import batched

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import ADMIN_IDS
from controllers.user import UserController
from handlers.administration.settings import (
    SendNotificationStates,
    NotificationTypeEnum,
)
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class NotificationTextHandler(BaseMessageHandler):
    batch_size: int = 20  # never more than 30! Read docs

    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            state=SendNotificationStates.handle_text,
            content_types=["text", "photo"],
            func=lambda message: message.chat.id in ADMIN_IDS,
            chat_types=["private"],
        )

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        async with state.data() as data:
            notification_type = data["notification_type"]
            custom_filter = data.get("custom_filter", "")
        await state.delete()

        if notification_type == NotificationTypeEnum.custom_filter.value:
            try:
                user_ids = await UserController.get_user_ids_by_custom_filter(
                    custom_filter, session
                )
            except ProgrammingError as e:
                await self.bot.send_message(
                    message.chat.id, f"Неправильный фильтр - {e}"
                )
                await state.delete()
                return
        else:
            user_ids = await UserController.get_user_ids_to_send_notifications(
                notification_type, session
            )

        total_count = len(user_ids)
        await self.bot.send_message(
            message.chat.id, f"Начинаем отправлять нотификации. Всего - {total_count}."
        )
        counter = 0
        for user_ids_batch in batched(user_ids, self.batch_size):
            for user_id in user_ids_batch:
                try:
                    if message.content_type == "photo":
                        await self.bot.send_photo(
                            user_id, message.photo[-1].file_id, message.caption
                        )
                    else:
                        await self.bot.send_message(user_id, message.text)
                except ApiTelegramException as e:
                    print(e)
                    pass
            counter += len(user_ids_batch)
            await self.bot.send_message(message.chat.id, f"{counter}/{total_count}")
            await asyncio.sleep(1)
        await self.bot.send_message(message.chat.id, "Все нотификации отправлены")
