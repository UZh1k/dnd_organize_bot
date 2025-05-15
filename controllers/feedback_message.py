from controllers.crud import CRUD
from models import FeedbackMessage


class FeedbackMessageController(CRUD):
    model = FeedbackMessage
