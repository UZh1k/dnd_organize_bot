from sqlalchemy.ext.asyncio import AsyncSession

from controllers.crud import CRUD
from models.user import User


class UserController(CRUD):
    model = User

    @classmethod
    async def get_by_id_or_username(
        cls, identifier: str, session: AsyncSession
    ) -> User | None:
        if identifier.isdigit():
            return await cls.get_one(int(identifier), session)
        else:
            return await cls.get_one(identifier, session, "username")
