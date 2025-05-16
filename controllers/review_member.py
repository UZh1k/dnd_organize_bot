from controllers.crud import CRUD
from models import ReviewMember


class ReviewMemberController(CRUD):
    model = ReviewMember
