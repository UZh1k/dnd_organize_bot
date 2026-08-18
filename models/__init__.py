from models.base import Base
from models.city import *
from models.feedback_message import *
from models.game import *
from models.game_application import *
from models.game_application_message import *
from models.game_member import *
from models.game_tag import *
from models.review import *
from models.review_member import *
from models.user import *

Base.registry.configure()
