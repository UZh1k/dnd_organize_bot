from controllers.crud import CRUD
from models import GameTag


class GameTagController(CRUD):
    model = GameTag
