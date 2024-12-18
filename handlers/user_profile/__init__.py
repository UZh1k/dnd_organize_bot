from handlers.user_profile.profile import handle_get_profile
from utils.handler.base_handler import BaseHandler


class UserProfileHandler(BaseHandler):
    def register_handlers(self):
        self.bot.register_message_handler(
            handle_get_profile,
            chat_types=["private"],
            commands=["profile"],
            pass_bot=True,
        )