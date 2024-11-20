from abc import abstractmethod

from telebot.async_telebot import AsyncTeleBot


class BaseHandler:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    @abstractmethod
    def register_handlers(self):
        ...
