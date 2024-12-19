from handlers.user_profile.states import UserProfileStates
from handlers.user_registration import UserRegistrationBio


class UserProfileBio(UserRegistrationBio):
    state = UserProfileStates.bio
