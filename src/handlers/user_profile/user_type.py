from src.handlers.user_profile.states import UserProfileStates
from src.handlers.user_registration import UserRegistrationUserType


class UserProfileUserType(UserRegistrationUserType):
    state = UserProfileStates.user_type
