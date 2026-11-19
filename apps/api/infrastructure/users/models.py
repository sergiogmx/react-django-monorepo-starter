from django.db import models


class UserProfileModel(models.Model):
    subject = models.CharField(max_length=255, unique=True)
    # Django convention: empty string, not NULL. The repository maps "" <-> None.
    email = models.EmailField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_profiles"
        verbose_name = "user profile"

    def __str__(self) -> str:
        return self.email or self.subject
