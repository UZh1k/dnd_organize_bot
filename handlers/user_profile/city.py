from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.user_profile.states import UserProfileStates
from handlers.user_registration import UserRegistrationCity
from models import User
from utils.other import CITY_TO_TIMEZONE


class UserProfileCity(UserRegistrationCity):
    state = UserProfileStates.city

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
        if known_timezone := CITY_TO_TIMEZONE.get(answer):
            user.timezone = known_timezone
        await session.refresh(user)
        await self.next_step(
            chat_id, user, session, bot, state, self.form_prefix, **kwargs
        )
