from sqlalchemy.ext.asyncio import AsyncSession

from handlers.user_registration.states import RegistrationStates
from models import User
from utils.form_text_item import FormTextItem


class UserRegistrationBio(FormTextItem):
    state = RegistrationStates.bio
    prepare_text = "Напиши кратко о себе"

    async def save_answer(self, text: str, user: User, session: AsyncSession):
        user.bio = text
