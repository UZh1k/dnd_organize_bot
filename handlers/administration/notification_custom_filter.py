from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import ADMIN_IDS
from handlers.administration.settings import SendNotificationStates
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class NotificationCustomFilterHandler(BaseMessageHandler):

    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_text,
            state=SendNotificationStates.custom_filter,
            content_types=["text"],
            func=lambda message: message.chat.id in ADMIN_IDS,
            chat_types=["private"],
        )
        self.bot.register_message_handler(
            self.handle_document,
            state=SendNotificationStates.custom_filter,
            content_types=["document"],
            func=lambda message: message.chat.id in ADMIN_IDS,
            chat_types=["private"],
        )

    async def handle_text(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        await self.save_filter(message, state, message.text)

    async def handle_document(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        document = message.document
        if not document.file_name or not document.file_name.lower().endswith(".txt"):
            await self.bot.send_message(message.chat.id, "Пришли файл в формате .txt.")
            return

        file_info = await self.bot.get_file(document.file_id)
        file_content = await self.bot.download_file(file_info.file_path)
        try:
            custom_filter = file_content.decode("utf-8-sig").strip()
        except UnicodeDecodeError:
            await self.bot.send_message(
                message.chat.id, "Не удалось прочитать файл. Сохрани его в UTF-8."
            )
            return

        if not custom_filter:
            await self.bot.send_message(message.chat.id, "Файл пустой.")
            return

        await self.save_filter(message, state, custom_filter)

    async def save_filter(
        self, message: Message, state: StateContext, custom_filter: str
    ):
        await self.bot.send_message(
            message.chat.id,
            "Напиши сообщение, которое отправится всем, "
            "кого ты выбрал (без дупликатов)",
        )
        await state.set(SendNotificationStates.handle_text)
        await state.add_data(custom_filter=custom_filter)
