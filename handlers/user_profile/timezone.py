from handlers.user_profile.states import UserProfileStates
from handlers.user_registration import UserRegistrationTimezone


class UserProfileTimezone(UserRegistrationTimezone):
    state = UserProfileStates.timezone
