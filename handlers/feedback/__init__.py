from handlers.feedback.funcs import handle_feedback, forward_to_admins, FeedbackStates
from utils.handler_groups.base_handler_group import BaseHandlerGroup
from utils.other import is_command


class FeedbackHandlerGroup(BaseHandlerGroup):
    def register_handlers(self):
        self.bot.register_message_handler(
            handle_feedback,
            chat_types=["private"],
            commands=["feedback"],
            pass_bot=True,
        )
        self.bot.register_message_handler(
            forward_to_admins,
            func=lambda message: not message.text or not is_command(message.text),
            state=FeedbackStates.get_feedback,
            content_types=["text", "photo", "document", "video"],
            pass_bot=True,
        )