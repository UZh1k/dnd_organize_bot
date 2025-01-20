from src.controllers.crud import CRUD
from src.models import GameTagLink


class GameTagLinkController(CRUD):
    model = GameTagLink
