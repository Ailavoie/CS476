from django.contrib import admin
from .models import User, ClientProfile, TherapistProfile, ConnectionRequest

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
        "connection_code",
    )

@admin.register(ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "therapist",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at",
        "therapist",
    )
    # Allows easy searching by client name or email
    search_fields = (
        "client__first_name",
        "client__last_name",
        "client__user__email",
        "therapist__last_name",
    )
    # Fields that can be directly edited from the list view (if status needs quick changes)
    list_editable = ("status",)