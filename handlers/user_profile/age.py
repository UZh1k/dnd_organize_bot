from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.user_profile.accept_minor import UserProfileAcceptMinor
from handlers.user_profile.states import UserProfileStates
from handlers.user_registration import UserRegistrationAge
from models import User


class UserProfileAge(UserRegistrationAge):
    state = UserProfileStates.age

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        **kwargs,
    ):
        if int(answer) < 18:
            await UserProfileAcceptMinor.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
        else:
            await self.next_step(
                chat_id, user, session, bot, state, self.form_prefix, **kwargs
            )
