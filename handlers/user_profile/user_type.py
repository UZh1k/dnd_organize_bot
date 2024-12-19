from handlers.user_profile.states import UserProfileStates
from handlers.user_registration import UserRegistrationUserType


class UserProfileUserType(UserRegistrationUserType):
    state = UserProfileStates.user_type
