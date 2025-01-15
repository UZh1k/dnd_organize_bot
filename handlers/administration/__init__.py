from handlers.administration.ban import BanHandler
from handlers.administration.ban_game import BanGameHandler
from handlers.administration.unban import UnbanHandler
from utils.handler_groups.base_handler_group import BaseHandlerGroup


class AdministrationHandlerGroup(BaseHandlerGroup):
    handlers = [BanHandler, UnbanHandler, BanGameHandler]
