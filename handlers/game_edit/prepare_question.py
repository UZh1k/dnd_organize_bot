from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.game import GameController
from handlers.game_edit import GameEditPlatform
from handlers.game_edit.form_items import (
    GameEditTitle,
    GameEditFormat,
    GameEditCity,
    GameEditSystem,
    GameEditDndRedaction,
    GameEditDndSetting,
    GameEditRedactionAndSetting,
    GameEditType,
    GameEditDescription,
    GameEditStartLevel,
    GameEditPlayersCount,
    GameEditFree,
    GameEditTime,
    GameEditPlayersAge,
    GameEditTechRequirements,
    GameEditTag,
    GameEditImage,
)
from handlers.game_edit.settings import (
    GameEditOptions,
    GAME_EDIT_FORM_PREFIX,
    GameEditCallbackPrefixes,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler

game_edit_option_handler_map = {
    GameEditOptions.title.value: GameEditTitle,
    GameEditOptions.format.value: GameEditFormat,
    GameEditOptions.city.value: GameEditCity,
    GameEditOptions.platform.value: GameEditPlatform,
    GameEditOptions.system.value: GameEditSystem,
    GameEditOptions.dnd_redaction.value: GameEditDndRedaction,
    GameEditOptions.dnd_setting.value: GameEditDndSetting,
    GameEditOptions.redaction_and_setting.value: GameEditRedactionAndSetting,
    GameEditOptions.type.value: GameEditType,
    GameEditOptions.description.value: GameEditDescription,
    GameEditOptions.start_level.value: GameEditStartLevel,
    GameEditOptions.players_count.value: GameEditPlayersCount,
    GameEditOptions.free.value: GameEditFree,
    GameEditOptions.time.value: GameEditTime,
    GameEditOptions.players_age.value: GameEditPlayersAge,
    GameEditOptions.tech_requirements.value: GameEditTechRequirements,
    GameEditOptions.image.value: GameEditImage,
    GameEditOptions.tag.value: GameEditTag,
}


class PrepareQuestionHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data.startswith(
                f"{GAME_EDIT_FORM_PREFIX}:"
                f"{GameEditCallbackPrefixes.choose_option.value}"
            ),
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        question = call.data.split(":")[-1]

        handler = game_edit_option_handler_map[question]

        tag_ids = []
        if question == GameEditOptions.tag.value:
            async with state.data() as data:
                game_id = data["game_id"]

            game = await GameController.get_one(game_id, session)
            tag_ids = [tag.id for tag in game.tags]
            await state.add_data(tags=tag_ids)

        await handler.prepare(
            call.message.chat.id,
            user,
            session,
            self.bot,
            state,
            GAME_EDIT_FORM_PREFIX,
            chosen_tags=tag_ids,
        )
