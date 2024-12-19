from handlers.game_application.accept_form import (
    handle_decline_application,
    ACCEPT_FORM_CALLBACK_PREFIX,
    ApplyAnswer, handle_accept_application,
)
from handlers.game_application.form import handle_apply_for_game, \
    GAME_APPLICATION_NO_DATA, GAME_APPLICATION_CANCEL
from handlers.game_application.handle_form import (
    handle_application_letter_no_data,
    handle_application_letter, handle_application_cancel,
)
from handlers.game_application.states import GameApplicationStates
from utils.handler.base_handler_group import BaseHandlerGroup


class GameApplicationHandler(BaseHandlerGroup):
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
            func=lambda call: call.data == GAME_APPLICATION_NO_DATA,
            pass_bot=True,
        )
        self.bot.register_callback_query_handler(
            handle_application_cancel,
            func=lambda call: call.data == GAME_APPLICATION_CANCEL,
            pass_bot=True,
        )
        self.bot.register_message_handler(
            handle_application_letter,
            state=GameApplicationStates.letter,
            pass_bot=True,
        )

        self.bot.register_callback_query_handler(
            handle_decline_application,
            func=lambda call: (
                call.data.split(":")[0] == ACCEPT_FORM_CALLBACK_PREFIX
                and call.data.split(":")[-1] == ApplyAnswer.no.value
            ),
            pass_bot=True,
        )
        self.bot.register_callback_query_handler(
            handle_accept_application,
            func=lambda call: (
                call.data.split(":")[0] == ACCEPT_FORM_CALLBACK_PREFIX
                and call.data.split(":")[-1] == ApplyAnswer.yes.value
            ),
            pass_bot=True,
        )
