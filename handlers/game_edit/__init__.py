from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery, InlineKeyboardButton, InputMediaPhoto, Message

from consts import MAX_ACTIVE_GAMES, NEWS_CHANNEL_ID
from controllers.game import GameController
from controllers.game_member import GameMemberController
from controllers.game_tag import GameTagController
from handlers.game_edit.cancel import CancelEditHandler
from handlers.game_edit.delete_ask import DeleteAskGameHandler
from handlers.game_edit.delete_confirm import DeleteConfirmGameHandler
from handlers.game_edit.edit_confirm import GameEditConfirmHandler
from handlers.game_edit.form_items import (
    GameEditAboutPrice,
    GameEditAcceptCity,
    GameEditAcceptOffline,
    GameEditCity,
    GameEditDescription,
    GameEditDndRedaction,
    GameEditDndSetting,
    GameEditFormat,
    GameEditFree,
    GameEditImage,
    GameEditPlayersAge,
    GameEditPlayersCount,
    GameEditRedactionAndSetting,
    GameEditStartLevel,
    GameEditSystem,
    GameEditTag,
    GameEditTechRequirements,
    GameEditTime,
    GameEditTitle,
    GameEditType,
)
from handlers.game_edit.form_items.platform import GameEditPlatform
from handlers.game_edit.prepare_question import PrepareQuestionHandler
from handlers.game_edit.settings import (
    GAME_EDIT_FORM_PREFIX,
    GameEditActions,
    GameEditCallbackPrefixes,
    GameShowStates,
)
from handlers.game_edit.show_game import ShowGameHandler
from models import User
from utils.form.form_item_group import FormItemGroup
from utils.game_text import create_game_markup, create_game_text
from utils.handler_groups.base_handler_group import BaseHandlerGroup
from utils.handler_groups.registration_handler_group import RegistrationHandlerGroup
from utils.message_helpers import get_pagination_row


class GameEditHandlerGroup(RegistrationHandlerGroup):
    page_size = 10
    handlers = [
        CancelEditHandler,
        ShowGameHandler,
        DeleteAskGameHandler,
        DeleteConfirmGameHandler,
        GameEditConfirmHandler,
        PrepareQuestionHandler,
    ]
    form_item_groups: tuple[FormItemGroup] = (
        FormItemGroup(main=GameEditTitle),
        FormItemGroup(
            main=GameEditFormat,
            side=(
                GameEditAcceptOffline,
                GameEditAcceptCity,
                GameEditCity,
                GameEditPlatform,
            ),
        ),
        FormItemGroup(main=GameEditCity),
        FormItemGroup(main=GameEditPlayersCount),
        FormItemGroup(main=GameEditFree, side=(GameEditAboutPrice,)),
        FormItemGroup(main=GameEditTime),
        FormItemGroup(main=GameEditSystem),
        FormItemGroup(main=GameEditDndRedaction),
        FormItemGroup(main=GameEditDndSetting),
        FormItemGroup(main=GameEditRedactionAndSetting),
        FormItemGroup(main=GameEditType),
        FormItemGroup(main=GameEditStartLevel),
        FormItemGroup(main=GameEditDescription),
        FormItemGroup(main=GameEditPlayersAge),
        FormItemGroup(main=GameEditTechRequirements),
        FormItemGroup(main=GameEditImage),
        FormItemGroup(main=GameEditTag),
    )
    command: str = "edit"
    form_prefix: str = GAME_EDIT_FORM_PREFIX

    edit_option_handler_map = {}

    def create_games_markup(self, games, page: int, total_count: int):
        games_markup = tuple(
            (
                f"🔎 {game.title}" if game.group_id is not None else game.title,
                str(game.id),
            )
            for game in games
        )
        markup = self.create_markup(
            games_markup,
            GameEditCallbackPrefixes.choose_game.value,
            row_width=1,
        )
        markup.add(
            *get_pagination_row(
                page,
                total_count,
                self.page_size,
                f"{self.form_prefix}:{GameEditCallbackPrefixes.page.value}",
            ),
            row_width=2,
        )
        markup.add(
            InlineKeyboardButton(
                "Отмена",
                callback_data=(
                    f"{self.form_prefix}:"
                    f"{GameEditCallbackPrefixes.choose_game.value}:"
                    f"{GameEditActions.cancel.value}"
                ),
            )
        )
        return markup

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
        games, total_count = await GameController.get_games_for_edit(
            user.id, session, self.page_size
        )
        if not games:
            await bot.send_message(
                message.chat.id,
                "Не нашёл созданных тобой игр. Выбери в меню “Создание игры” "
                "или воспользуйся командой /create.",
            )
            return

        active_games_count = await GameController.get_active_games_count(
            user.id, session
        )
        active_games_text = (
            f"Активных наборов: {active_games_count} из {MAX_ACTIVE_GAMES}."
        )
        if active_games_count >= MAX_ACTIVE_GAMES:
            active_games_text += (
                "\n\n🔴 Лимит достигнут. Чтобы опубликовать новую игру, "
                "удали здесь одну из активных игр или закрой набор командой "
                "/close в чате соответствующей игры."
            )

        await state.set(GameShowStates.show_games)
        markup = self.create_games_markup(games, 0, total_count)
        await bot.send_message(
            message.chat.id,
            f"{active_games_text}\n\nВыбери, какую игру ты хочешь отредактировать.",
            reply_markup=markup,
        )

    async def show_games_page(
        self,
        call: CallbackQuery,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        page = int(call.data.split(":")[-1])
        games, total_count = await GameController.get_games_for_edit(
            user.id, session, self.page_size, page
        )
        if not games:
            page = max(0, (total_count - 1) // self.page_size)
            games, total_count = await GameController.get_games_for_edit(
                user.id, session, self.page_size, page
            )
        await bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=self.create_games_markup(games, page, total_count),
        )
        await bot.answer_callback_query(call.id)

    async def last_step(
        self,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        form_prefix: str,
        **kwargs,
    ):
        async with state.data() as data:
            game = await GameController.get_one(data["game_id"], session)

        if not game or game.creator_id != user.id or not game.active:
            await bot.send_message(chat_id, "Игра уже не активна")
            return

        tag_ids = data.pop("tags", None)
        for key, value in data.items():
            if hasattr(game, key):
                setattr(game, key, value)

        if tag_ids is not None:
            new_tags = await GameTagController.get_list(session, ids=tag_ids)
            game.tags = new_tags

        await session.flush()
        await session.refresh(game)
        await ShowGameHandler.show_game_with_markup(chat_id, game, bot)

        reset_image = data.get("image")
        await state.reset_data()
        await state.add_data(game_id=game.id)

        if game.post_id:
            players_count = await GameMemberController.count_game_members(
                game.id, session
            )
            game_text = create_game_text(game, players_count=players_count)
            try:
                if reset_image:
                    await bot.edit_message_media(
                        InputMediaPhoto(game.image, game_text, parse_mode="Markdown"),
                        NEWS_CHANNEL_ID,
                        game.post_id,
                        reply_markup=await create_game_markup(game, session),
                    )
                else:
                    await bot.edit_message_caption(
                        game_text,
                        NEWS_CHANNEL_ID,
                        game.post_id,
                        parse_mode="Markdown",
                        reply_markup=await create_game_markup(game, session),
                    )
            except ApiTelegramException:
                pass

    def register_handlers(self):
        BaseHandlerGroup.register_handlers(self)

        self.bot.register_message_handler(
            self.first_step,
            chat_types=["private"],
            commands=[self.command],
            pass_bot=True,
        )

        self.bot.register_callback_query_handler(
            self.show_games_page,
            func=lambda call: call.data.startswith(
                f"{self.form_prefix}:{GameEditCallbackPrefixes.page.value}:"
            ),
            pass_bot=True,
        )

        for current_item_group in self.form_item_groups:
            for current_item in (current_item_group.main, *current_item_group.side):
                self.register_form_handlers(
                    current_item(self.last_step, self.form_prefix)
                )
