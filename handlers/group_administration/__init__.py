from consts import BOT_USERNAME
from handlers.group_administration.group_funcs import (
    handle_bot_added_to_group,
    handle_bot_removed_group,
)
from handlers.group_administration.link_game import (
    handle_bot_promoted_to_admin,
    handle_link_game_command,
    handle_link_game,
    GAME_LINK_PREFIX,
)
from utils.handler.base_handler import BaseHandler


class GroupAdministrationHandler(BaseHandler):
    def register_handlers(self):
        self.bot.register_my_chat_member_handler(
            handle_bot_added_to_group,
            lambda update: (
                update.new_chat_member.user.username == BOT_USERNAME
                and update.new_chat_member.status == "member"
            ),
            pass_bot=True,
        )

        self.bot.register_my_chat_member_handler(
            handle_bot_promoted_to_admin,
            lambda update: (
                update.new_chat_member.user.username == BOT_USERNAME
                and update.new_chat_member.status == "administrator"
            ),
            pass_bot=True,
        )
        self.bot.register_message_handler(
            handle_link_game_command,
            commands=["link"],
            chat_types=["group", "supergroup"],
            pass_bot=True,
        )
        self.bot.register_callback_query_handler(
            handle_link_game,
            lambda call: call.data.startswith(GAME_LINK_PREFIX),
            pass_bot=True,
        )

        self.bot.register_my_chat_member_handler(
            handle_bot_removed_group,
            lambda update: (
                update.new_chat_member.user.username == BOT_USERNAME
                and update.new_chat_member.status == "left"
            ),
            pass_bot=True,
        )
