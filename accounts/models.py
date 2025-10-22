import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=False
    )
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def is_client(self):
        return hasattr(self, "client_profile")

    @property
    def is_therapist(self):
        return hasattr(self, "therapist_profile")

    def __str__(self):
        return self.email

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")

    date_of_birth = models.DateField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    therapist = models.ForeignKey(
        "TherapistProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="clients"
    )

    def __str__(self):
        return f"Client: {self.first_name} {self.last_name}"


class TherapistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="therapist_profile")

    date_of_birth = models.DateField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50)
    specialty = models.CharField(max_length=100)

    country = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    street = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    rating = models.FloatField(default=0.0)

    connection_code = models.CharField(max_length=8, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.connection_code:
            self.connection_code = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Therapist: {self.first_name} {self.last_name}"

class ConnectionRequest(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="sent_requests")
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(
        max_length=10,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} → {self.therapist} ({self.status})"
