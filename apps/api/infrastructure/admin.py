from django.contrib import admin

from infrastructure.users.models import UserProfileModel


@admin.register(UserProfileModel)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["subject", "email", "created_at"]
    search_fields = ["subject", "email"]
    readonly_fields = ["subject", "created_at"]
