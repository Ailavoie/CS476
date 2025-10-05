from django.contrib import admin
from .models import User, ClientProfile, TherapistProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_staff")

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "date_of_birth",
        "country",
        "province",
        "phone_number",
        "therapist",
    )


@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "license_number",
        "specialty",
        "country",
        "province",
        "phone_number",
    )

