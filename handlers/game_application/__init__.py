from handlers.game_application.form import handle_apply_for_game
from handlers.game_application.handle_form import (
    handle_application_letter_no_data,
    handle_application_letter,
)
from handlers.game_application.states import GameApplicationStates
from utils.handler.base_handler import BaseHandler


class GameApplicationHandler(BaseHandler):
    def register_handlers(self):
        self.bot.register_message_handler(
            handle_apply_for_game,
            chat_types=["private"],
            commands=["start"],
            func=lambda message: len(message.text.split()) == 2,
            pass_bot=True,
        )
        self.bot.register_callback_query_handler(
            handle_application_letter_no_data,
            func=lambda call: call.data == "GameApplication:no_data",
            pass_bot=True,
        )
        self.bot.register_message_handler(
            handle_application_letter,
            state=GameApplicationStates.letter,
            pass_bot=True,
        )
