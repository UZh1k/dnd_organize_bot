from abc import ABC
from typing import Type

from telebot.async_telebot import AsyncTeleBot

from utils.handlers.base_handler import BaseHandler


class BaseHandlerGroup(ABC):
    handlers: list[Type[BaseHandler]] = []

    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    def register_handlers(self):
        for handler in self.handlers:
            handler(self.bot).register_handler()
