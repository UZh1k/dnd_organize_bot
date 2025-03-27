from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.review import ReviewController
from handlers.game_application.form import GAME_APPLICATION_CALLBACK_PREFIX
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup, generate_review_text


class ApplicantReviewHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(f"{GAME_APPLICATION_CALLBACK_PREFIX}:reviews")
            ),
        )

    async def check_callback_not_processed(self, call: CallbackQuery) -> bool:
        try:
            if len(call.data.split(":")) == 4:
                markup = None
                if call.data.split(":")[2] == "dm":
                    markup = create_markup(
                        (
                            ("Написать сопроводительное сообщение", "letter"),
                            ("Отправить заявку без сообщения", "no_data"),
                            ("Отмена", "cancel"),
                        ),
                        GAME_APPLICATION_CALLBACK_PREFIX,
                    )
                elif call.data.split(":")[2] == "player":
                    markup = call.message.reply_markup
                    markup.keyboard.pop()
                await self.bot.edit_message_reply_markup(
                    call.message.chat.id, call.message.message_id, reply_markup=markup
                )
            return True
        except ApiTelegramException:
            return False

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        first_message = False
        call_data_split = call.data.split(":")
        if len(call_data_split) == 5:
            review_num = int(call_data_split[-1])
        else:
            first_message = True
            review_num = 0

        user_id = int(call_data_split[3])
        receiver_type = call_data_split[2]
        reviews = await ReviewController.get_user_reviews(
            user_id, session, receiver_type
        )

        if not reviews:
            await self.bot.send_message(call.message.chat.id, "Пока нет отзывов")
            return

        buttons = []
        if review_num != 0:
            buttons.append(("Предыдущий", f"{review_num - 1}"))
        if review_num != len(reviews) - 1:
            buttons.append(("Следующий", f"{review_num + 1}"))

        keyboard = create_markup(
            buttons,
            f"{GAME_APPLICATION_CALLBACK_PREFIX}:reviews:{receiver_type}:{user_id}",
            row_width=2,
        )

        review = reviews[review_num]
        review_text = generate_review_text(review, review_num, len(reviews))

        if first_message:
            await self.bot.send_message(
                call.message.chat.id, review_text, reply_markup=keyboard
            )
        else:
            await self.bot.edit_message_text(
                review_text,
                call.message.chat.id,
                call.message.id,
                reply_markup=keyboard,
            )
