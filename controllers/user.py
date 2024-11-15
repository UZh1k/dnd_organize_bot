from controllers.crud import CRUD
from models.user import User


class UserController(CRUD):
    model = User
