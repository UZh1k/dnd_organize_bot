from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from controllers.game import GameController
from controllers.game_application import GameApplicationController
from controllers.game_application_message import GameApplicationMessageController
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class AnswerApplicationHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            content_types=[
                "text",
                "photo",
                "voice",
                "audio",
                "video_note",
            ],
            func=lambda message: message.reply_to_message,
            chat_types=["private"],
        )

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        if application := await GameApplicationController.get_one_for_answer(
            user.id, message.reply_to_message.id, session
        ):
            game_id = application.game_id
            receiver_id = application.user_id
        elif application_message := await GameApplicationMessageController.get_one_for_answer(
            user.id, message.reply_to_message.id, session
        ):
            game_id = application_message.game_id
            receiver_id = application_message.sender_id
        else:
            return

        game = await GameController.get_one(game_id, session)
        await self.bot.send_message(
            receiver_id,
            f'Ответ от {"мастера" if user.id == game.creator_id else "игрока"} '
            f'{user.name} по игре "{game.title}". \n\n'
            "Чтобы переслать ему что-то, ответь на сообщение ниже. "
            "В сообщении можно прикрепить фото, войс или кружок.",
        )
        answer_message_id = await self.bot.copy_message(
            receiver_id,
            message.chat.id,
            message.id,
        )

        await self.bot.send_message(message.chat.id, "Сообщение отправлено")

        await GameApplicationMessageController.create(
            {
                "sender_id": user.id,
                "receiver_id": receiver_id,
                "game_id": game_id,
                "message_id": answer_message_id.message_id,
            },
            session,
        )
