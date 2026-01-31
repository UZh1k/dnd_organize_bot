from handlers.administration.ban import BanHandler
from handlers.administration.ban_game import BanGameHandler
from handlers.administration.cancel import CancelHandler
from handlers.administration.close_game import CloseGameHandler
from handlers.administration.handle_notification_text import NotificationTextHandler
from handlers.administration.handle_notification_type import NotificationTypeHandler
from handlers.administration.notification_custom_filter import (
    NotificationCustomFilterHandler,
)
from handlers.administration.send_notification import SendNotificationHandler
from handlers.administration.unban import UnbanHandler
from utils.handler_groups.base_handler_group import BaseHandlerGroup


class AdministrationHandlerGroup(BaseHandlerGroup):
    handlers = [
        CancelHandler,
        BanHandler,
        UnbanHandler,
        BanGameHandler,
        SendNotificationHandler,
        NotificationTypeHandler,
        NotificationCustomFilterHandler,
        NotificationTextHandler,
        CloseGameHandler,
    ]
