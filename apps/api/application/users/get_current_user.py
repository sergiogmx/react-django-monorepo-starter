from domain.users import Identity, UserProfile, UserProfileRepository


class GetCurrentUser:
    """Use case: return the caller's profile, provisioning it on first use."""

    def __init__(self, profiles: UserProfileRepository) -> None:
        self._profiles = profiles

    def execute(self, identity: Identity) -> UserProfile:
        return self._profiles.get_or_create(identity)
