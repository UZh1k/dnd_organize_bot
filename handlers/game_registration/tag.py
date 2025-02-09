from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from controllers.game_tag import GameTagController
from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_item import FormChoiceItem


class GameRegistrationTag(FormChoiceItem):
    state = GameRegistrationStates.tag
    prepare_text = "Ты можешь выбрать теги, которые я добавлю к твоей публикации."
    form_item_name = "tag"
    max_tags_count = 5

    alert_message = None
    choices = (
        ("Сохранить", "save"),
        ("Нет", "no"),
    )

    @classmethod
    async def prepare_markup(
        cls, form_prefix: str, session: AsyncSession, chosen_tags: list[int] = None
    ):
        chosen_tags = chosen_tags or []
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "Сохранить", callback_data=cls.gen_callback_data("save", form_prefix)
            )
        )
        tags = await GameTagController.get_list(session)
        markup.add(
            *(
                InlineKeyboardButton(
                    f"#{tag.title}{'✅' if tag.id in chosen_tags else ''}",
                    callback_data=cls.gen_callback_data(tag.id, form_prefix),
                )
                for tag in tags
            ),
            row_width=2,
        )
        return markup

    async def handle_callback(
        self,
        call: CallbackQuery,
        bot: AsyncTeleBot,
        user: User,
        session: AsyncSession,
        state: StateContext,
    ):
        text = call.data.split(":")[-1]
        async with state.data() as data:
            chosen_tags = data.get("tags", [])

        if text == "save":
            await bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=None
            )
            await state.add_data(tags=chosen_tags)
            await self.on_answered(
                text, call.message.chat.id, user, session, bot, state
            )
        else:
            tag_id = int(text)
            if tag_id not in chosen_tags:
                if len(chosen_tags) >= self.max_tags_count:
                    await bot.answer_callback_query(
                        callback_query_id=call.id,
                        text=f"Максимум {self.max_tags_count} тегов",
                    )
                    return
                chosen_tags.append(tag_id)
                await bot.answer_callback_query(
                    callback_query_id=call.id, text="Тег добавлен"
                )
            else:
                chosen_tags.remove(tag_id)
                await bot.answer_callback_query(
                    callback_query_id=call.id, text="Тег удален"
                )

            await state.add_data(tags=chosen_tags)
            try:
                await bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=await self.prepare_markup(
                        self.form_prefix, session, chosen_tags=chosen_tags
                    ),
                )
            except ApiTelegramException:
                pass
