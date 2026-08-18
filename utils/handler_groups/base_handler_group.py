from abc import ABC

from telebot.async_telebot import AsyncTeleBot

from utils.handlers.base_handler import BaseHandler


# ABC here is a "don't instantiate this directly" marker for the subclass-per-feature
# pattern; the base intentionally has no abstract members, only concrete behaviour.
class BaseHandlerGroup(ABC):  # noqa: B024
    handlers: list[type[BaseHandler]] = []

    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    def register_handlers(self):
        for handler in self.handlers:
            handler(self.bot).register_handler()
