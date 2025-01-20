from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from controllers.game import GameController
from handlers.game_edit.settings import GameEditCallbackPrefixes, GAME_EDIT_FORM_PREFIX
from models import User
from utils.form.form_item_group import FormItemGroup
from utils.handler_groups.registration_handler_group import RegistrationHandlerGroup


class GameEditHandlerGroup(RegistrationHandlerGroup):
    form_item_groups: tuple[FormItemGroup] = ()
    command: str = "edit"
    form_prefix: str = GAME_EDIT_FORM_PREFIX

    edit_option_handler_map = {}

    async def first_step(
        self,
        message: Message,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await state.delete()
        if not user.registered:
            await bot.send_message(
                message.chat.id, "Не узнаю тебя. Ты точно зарегистрировался?"
            )
            return
        games = await GameController.get_games_for_edit(user.id, session)
        if not games:
            await bot.send_message(
                message.chat.id,
                "Не нашёл созданных тобой игр. Выбери в меню “Создание игры” "
                "или воспользуйся командой /create.",
            )
            return

        games_markup = tuple((game.title, str(game.id)) for game in games)
        markup = self.create_markup(
            games_markup,
            GameEditCallbackPrefixes.choose_game.value,
            row_width=1,
        )
        await bot.send_message(
            message.chat.id,
            "Выбери, у какой игры ты хочешь редактировать описание.",
            reply_markup=markup,
        )
