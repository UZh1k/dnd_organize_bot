from handlers.user_profile.states import UserProfileStates
from handlers.user_registration import UserRegistrationAcceptMinor


class UserProfileAcceptMinor(UserRegistrationAcceptMinor):
    state = UserProfileStates.accept_minor
