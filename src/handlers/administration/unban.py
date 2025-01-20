from telebot.types import Message, User

from src.consts import ADMIN_IDS
from src.handlers.administration.ban import BanHandler


class UnbanHandler(BanHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["unban"],
            func=lambda message: message.chat.id in ADMIN_IDS,
        )

    async def on_action(self, message: Message, user: User):
        user.banned = False
        await self.bot.send_message(message.chat.id, "Пользователь разбанен")
