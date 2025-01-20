from src.handlers.user_profile.states import UserProfileStates
from src.handlers.user_registration import UserRegistrationTimezone


class UserProfileTimezone(UserRegistrationTimezone):
    state = UserProfileStates.timezone
