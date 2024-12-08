from handlers.feedback.funcs import handle_feedback, forward_to_admins, FeedbackStates
from utils.handler.base_handler import BaseHandler


class FeedbackHandler(BaseHandler):
    def register_handlers(self):
        self.bot.register_message_handler(
            handle_feedback,
            chat_types=["private"],
            commands=["feedback"],
            pass_bot=True,
        )
        self.bot.register_message_handler(
            forward_to_admins,
            state=FeedbackStates.get_feedback,
            content_types=["text", "photo", "document", "video"],
            pass_bot=True,
        )