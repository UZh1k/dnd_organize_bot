from src.handlers.administration.ban import BanHandler
from src.handlers.administration.ban_game import BanGameHandler
from src.handlers.administration.unban import UnbanHandler
from src.utils.handler_groups.base_handler_group import BaseHandlerGroup


class AdministrationHandlerGroup(BaseHandlerGroup):
    handlers = [BanHandler, UnbanHandler, BanGameHandler]
