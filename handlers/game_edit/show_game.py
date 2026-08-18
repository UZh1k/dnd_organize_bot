from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.game import GameController
from handlers.game_edit.settings import (
    GAME_EDIT_FORM_PREFIX,
    GameEditActions,
    GameEditCallbackPrefixes,
)
from models import Game, User
from utils.game_text import create_game_text
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup, is_caption_too_long_error


class ShowGameHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data.startswith(
                f"{GAME_EDIT_FORM_PREFIX}:{GameEditCallbackPrefixes.choose_game.value}"
            ),
        )

    @classmethod
    async def show_game_with_markup(
        cls, chat_id: int, game: Game, bot: AsyncTeleBot
    ) -> str:
        text = create_game_text(game)
        try:
            await bot.send_photo(
                chat_id,
                game.image,
                text,
                parse_mode="Markdown",
            )
        except ApiTelegramException as error:
            if not is_caption_too_long_error(error):
                raise
            await bot.send_message(
                chat_id,
                "Описание игры получилось слишком длинным, поэтому я не могу "
                "показать его целиком. Сократи одно или несколько текстовых "
                "полей с помощью кнопки «Редактировать».",
            )

        markup = create_markup(
            (
                ("Редактировать", GameEditActions.edit.value),
                ("Удалить", GameEditActions.delete.value),
                ("Все ОК", GameEditActions.cancel.value),
            ),
            GameEditCallbackPrefixes.game_action.value,
            form_prefix=GAME_EDIT_FORM_PREFIX,
        )
        await bot.send_message(
            chat_id,
            f"Выбрана игра “{game.title}”. Ты хочешь что-то скорректировать?",
            reply_markup=markup,
        )
        return text

    async def handle_callback(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        try:
            await self.bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=None
            )
        except ApiTelegramException:
            return

        game_id = int(call.data.split(":")[-1])
        game = await GameController.get_one(game_id, session)

        if not game or game.creator_id != user.id or not game.active:
            await self.bot.send_message(call.message.chat.id, "Игра уже неактивна")
            return

        await state.add_data(game_id=game_id)

        await self.show_game_with_markup(call.message.chat.id, game, self.bot)
