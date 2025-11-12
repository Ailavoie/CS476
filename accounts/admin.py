from django.contrib import admin
from .models import ConnectionRequest, User, ClientProfile, TherapistProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_staff",)

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
        "twofa",
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
        "connection_code",
        "twofa",
    )

@admin.register(ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "therapist", "status", "created_at")
    list_filter = ("status", "therapist")
    search_fields = ("client__first_name", "client__last_name", "therapist__first_name", "therapist__last_name")