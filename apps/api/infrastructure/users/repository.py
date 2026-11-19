from domain.users import Identity, UserProfile
from infrastructure.users.models import UserProfileModel


class DjangoUserProfileRepository:
    """Implements domain.users.UserProfileRepository with the Django ORM."""

    def get_or_create(self, identity: Identity) -> UserProfile:
        # Django's get_or_create catches the IntegrityError raised when a
        # concurrent request inserts the same subject first, then re-reads it.
        model, _ = UserProfileModel.objects.get_or_create(
            subject=identity.subject,
            defaults={"email": identity.email or ""},
        )
        if identity.email and model.email != identity.email:
            model.email = identity.email
            model.save(update_fields=["email"])
        return _to_entity(model)


def _to_entity(model: UserProfileModel) -> UserProfile:
    return UserProfile(
        id=model.pk,
        subject=model.subject,
        email=model.email or None,
        created_at=model.created_at,
    )
