from enum import Enum
from typing import Final

GAME_EDIT_FORM_PREFIX: Final[str] = "GameEdit"

class GameEditCallbackPrefixes(Enum):
    choose_game = "choose_game"
