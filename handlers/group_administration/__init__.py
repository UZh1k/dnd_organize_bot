from consts import BOT_USERNAME
from handlers.group_administration.group_funcs import (
    handle_bot_added_to_group,
    handle_bot_removed_group,
    close_game,
    done_game,
)
from handlers.group_administration.link_game import (
    handle_bot_promoted_to_admin,
    handle_link_game_command,
    handle_link_game,
    GAME_LINK_PREFIX,
)
from handlers.group_administration.member_funcs import (
    handle_player_added_to_group,
    handle_player_left_group,
)
from handlers.group_administration.migration import handle_group_migrated
from handlers.group_administration.post_game import update_game_post
from utils.handler.base_handler_group import BaseHandlerGroup


class GroupAdministrationHandler(BaseHandlerGroup):
    def register_handlers(self):
        self.bot.register_my_chat_member_handler(
            handle_bot_added_to_group,
            lambda update: (
                update.chat.type in ["group", "supergroup"]
                and update.new_chat_member.user.username == BOT_USERNAME
                and update.new_chat_member.status == "member"
            ),
            pass_bot=True,
        )

        self.bot.register_my_chat_member_handler(
            handle_bot_promoted_to_admin,
            lambda update: (
                update.chat.type in ["group", "supergroup"]
                and update.new_chat_member.user.username == BOT_USERNAME
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
                update.chat.type in ["group", "supergroup"]
                and update.new_chat_member.user.username == BOT_USERNAME
                and update.new_chat_member.status in ["kicked", "left"]
            ),
            pass_bot=True,
        )

        self.bot.register_chat_member_handler(
            handle_player_added_to_group,
            lambda update: (
                update.chat.type in ["group", "supergroup"]
                and update.new_chat_member.status == "member"
                and not update.new_chat_member.user.is_bot
            ),
            pass_bot=True,
        )
        self.bot.register_chat_member_handler(
            handle_player_left_group,
            lambda update: (
                update.chat.type in ["group", "supergroup"]
                and update.new_chat_member.status in ["kicked", "left"]
            ),
            pass_bot=True,
        )

        self.bot.register_message_handler(
            close_game,
            commands=["close"],
            chat_types=["group", "supergroup"],
            pass_bot=True,
        )
        self.bot.register_message_handler(
            done_game,
            commands=["done"],
            chat_types=["group", "supergroup"],
            pass_bot=True,
        )
        self.bot.register_message_handler(
            update_game_post,
            commands=["update"],
            chat_types=["group", "supergroup"],
            pass_bot=True,
        )

        self.bot.register_message_handler(
            handle_group_migrated,
            content_types=["migrate_to_chat_id"],
            chat_types=["group", "supergroup"],
            pass_bot=True,
        )
