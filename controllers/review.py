from controllers.crud import CRUD
from models import Review


class ReviewController(CRUD):
    model = Review
