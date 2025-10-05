from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ClientProfile, TherapistProfile
from django.core.exceptions import ValidationError

class BaseRegisterForm(UserCreationForm):
    date_of_birth = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=False, help_text="(Optional)")
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data.get("last_name", "")
        user.save()
        return user


class ClientRegisterForm(BaseRegisterForm):
    country = forms.CharField(required=False, help_text="(Optional)")
    province = forms.CharField(required=False, help_text="(Optional)")
    street = forms.CharField(required=False, help_text="(Optional)")
    phone_number = forms.CharField(required=False, help_text="(Optional)")
    emergency_contact_name = forms.CharField(required=False, help_text="(Optional)")
    emergency_contact_phone = forms.CharField(required=False, help_text="(Optional)")


    class Meta(BaseRegisterForm.Meta):
        fields = BaseRegisterForm.Meta.fields + (
            "date_of_birth",
            "first_name",
            "last_name",
        )

    def save(self, commit=True):
        user = super().save(commit)
        ClientProfile.objects.create(
            user=user,
            date_of_birth=self.cleaned_data["date_of_birth"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data.get("last_name"),
            country=self.cleaned_data.get("country"),
            province=self.cleaned_data.get("province"),
            street=self.cleaned_data.get("street"),
            phone_number=self.cleaned_data.get("phone_number"),
            emergency_contact_name=self.cleaned_data.get("emergency_contact_name"),
            emergency_contact_phone=self.cleaned_data.get("emergency_contact_phone"),
        )
        return user

class TherapistRegisterForm(BaseRegisterForm):
    license_number = forms.CharField(required=True)
    specialty = forms.CharField(required=True)
    country = forms.CharField(required=True)
    province = forms.CharField(required=True)
    street = forms.CharField(required=False, help_text="(Optional)")
    phone_number = forms.CharField(required=False, help_text="(Optional)")

    class Meta(BaseRegisterForm.Meta):
        fields = BaseRegisterForm.Meta.fields + (
            "date_of_birth",
            "first_name",
            "last_name",
        )

    def save(self, commit=True):
        user = super().save(commit)
        TherapistProfile.objects.create(
            user=user,
            date_of_birth=self.cleaned_data["date_of_birth"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data.get("last_name"),
            license_number=self.cleaned_data["license_number"],
            specialty=self.cleaned_data["specialty"],
            country=self.cleaned_data["country"],
            province=self.cleaned_data["province"],
            street=self.cleaned_data.get("street"),
            phone_number=self.cleaned_data.get("phone_number"),
        )
        return user