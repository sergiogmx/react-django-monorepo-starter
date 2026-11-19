from django.test import TestCase

from domain.users import Identity
from infrastructure.users.models import UserProfileModel
from infrastructure.users.repository import DjangoUserProfileRepository


class DjangoUserProfileRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.repository = DjangoUserProfileRepository()

    def test_creates_a_profile_the_first_time(self) -> None:
        profile = self.repository.get_or_create(
            Identity("auth0|ana", "ana@example.com")
        )

        self.assertEqual(profile.subject, "auth0|ana")
        self.assertEqual(profile.email, "ana@example.com")
        self.assertEqual(UserProfileModel.objects.count(), 1)

    def test_reuses_the_existing_profile(self) -> None:
        first = self.repository.get_or_create(Identity("auth0|ana"))
        second = self.repository.get_or_create(Identity("auth0|ana"))

        self.assertEqual(first.id, second.id)
        self.assertEqual(UserProfileModel.objects.count(), 1)

    def test_returns_the_row_another_request_inserted_first(self) -> None:
        # Simulates losing the race: the row already exists when we arrive.
        UserProfileModel.objects.create(subject="auth0|ana")

        profile = self.repository.get_or_create(Identity("auth0|ana"))

        self.assertEqual(UserProfileModel.objects.count(), 1)
        self.assertEqual(profile.subject, "auth0|ana")

    def test_updates_the_email_when_the_token_brings_a_new_one(self) -> None:
        self.repository.get_or_create(Identity("auth0|ana"))

        profile = self.repository.get_or_create(
            Identity("auth0|ana", "ana@example.com")
        )

        self.assertEqual(profile.email, "ana@example.com")
