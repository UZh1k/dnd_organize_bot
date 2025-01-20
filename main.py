import asyncio
import logging

from telebot.asyncio_filters import StateFilter
from telebot.states.asyncio import StateMiddleware
import src.consts
from src.handlers.administration import AdministrationHandlerGroup
from src.handlers.feedback import FeedbackHandlerGroup
from src.handlers.game_application import GameApplicationHandlerGroup
from src.handlers.game_registration import GameRegistrationHandlerGroup
from src.handlers.group_administration import GroupAdministrationHandlerGroup
from src.handlers.user_profile import UserProfileHandlerGroup
from src.handlers.user_registration import UserRegistrationHandlerGroup
from src.middlewares.exception import ExceptionMiddleware
from src.middlewares.session import SessionMiddleware
from src.middlewares.user import UserMiddleware
from src.singleton.telegram import bot

AdministrationHandlerGroup(bot).register_handlers()
GroupAdministrationHandlerGroup(bot).register_handlers()
FeedbackHandlerGroup(bot).register_handlers()
GameApplicationHandlerGroup(bot).register_handlers()
UserRegistrationHandlerGroup(bot).register_handlers()
UserProfileHandlerGroup(bot).register_handlers()
GameRegistrationHandlerGroup(bot).register_handlers()
bot.add_custom_filter(StateFilter(bot))
bot.setup_middleware(SessionMiddleware())
bot.setup_middleware(UserMiddleware())
bot.setup_middleware(ExceptionMiddleware(bot))
bot.setup_middleware(StateMiddleware(bot))

if __name__ == "__main__":
    asyncio.run(
        bot.infinity_polling(
            allowed_updates=src.consts.ALLOWED_UPDATE_TYPES, logger_level=logging.INFO
        )
    )
