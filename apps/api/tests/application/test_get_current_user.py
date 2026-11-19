"""Use-case tests: plain unittest, fake repository, no Django and no database."""

from datetime import UTC, datetime
from unittest import TestCase

from application.users.get_current_user import GetCurrentUser
from domain.users import Identity, UserProfile


class InMemoryUserProfiles:
    def __init__(self) -> None:
        self.by_subject: dict[str, UserProfile] = {}

    def get_or_create(self, identity: Identity) -> UserProfile:
        if identity.subject not in self.by_subject:
            self.by_subject[identity.subject] = UserProfile(
                id=len(self.by_subject) + 1,
                subject=identity.subject,
                email=identity.email,
                created_at=datetime.now(UTC),
            )
        return self.by_subject[identity.subject]


class GetCurrentUserTests(TestCase):
    def setUp(self) -> None:
        self.profiles = InMemoryUserProfiles()
        self.use_case = GetCurrentUser(profiles=self.profiles)

    def test_provisions_a_profile_for_a_new_user(self) -> None:
        profile = self.use_case.execute(Identity("auth0|ana", "ana@example.com"))

        self.assertEqual(profile.subject, "auth0|ana")
        self.assertEqual(profile.email, "ana@example.com")
        self.assertEqual(len(self.profiles.by_subject), 1)

    def test_returns_the_same_profile_for_a_returning_user(self) -> None:
        first = self.use_case.execute(Identity("auth0|ana"))
        second = self.use_case.execute(Identity("auth0|ana"))

        self.assertEqual(first.id, second.id)
        self.assertEqual(len(self.profiles.by_subject), 1)
