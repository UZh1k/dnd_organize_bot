from models.base import Base
from models.city import *  # noqa: F403
from models.feedback_message import *  # noqa: F403
from models.game import *  # noqa: F403
from models.game_application import *  # noqa: F403
from models.game_member import *  # noqa: F403
from models.game_tag import *  # noqa: F403
from models.review import *  # noqa: F403
from models.review_member import *  # noqa: F403
from models.user import *  # noqa: F403

Base.registry.configure()
