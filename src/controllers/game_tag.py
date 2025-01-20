from src.controllers.crud import CRUD
from src.models import GameTag


class GameTagController(CRUD):
    model = GameTag
