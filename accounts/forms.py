from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ClientProfile, TherapistProfile, COUNTRY_CHOICES
from django.core.exceptions import ValidationError

class BaseRegisterForm(UserCreationForm):
    # Fields inherited by both forms
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
    # CRITICAL FIX: Add __init__ to dynamically prefix all inherited field IDs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # Apply prefix only if the ID hasn't been explicitly set with a unique prefix
            if 'id' not in field.widget.attrs:
                field.widget.attrs['id'] = f'id_client_{name}'
    
    # Custom fields (already have explicit unique IDs, which is good)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False, widget=forms.Select(attrs={'id': 'id_client_country', 'class': 'country-select'}))
    province = forms.ChoiceField(choices=[('', 'Select Country First')], required=False, widget=forms.Select(attrs={'id': 'id_client_province', 'class': 'province-select'}))
    street = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Street Address'}), help_text="(Optional)")
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
    

EXPERTISES = [

("Cognitive Behavioral Therapy", "Cognitive Behavioral Therapy"),
("Dialectical Behavior Therapy", "Dialectical Behavior Therapy"),
("Family Counseling", "Family Counseling"),

("Couples Therapy", "Couples Therapy"),

("Child & Adolescent Therapy", "Child & Adolescent Therapy"),

("Grief Counseling", "Grief Counseling"),

("Trauma-Focused Therapy", "Trauma-Focused Therapy"),

("Anxiety & Stress Management", "Anxiety & Stress Management"),

("Depression Therapy", "Depression Therapy"),

("Addiction & Substance Abuse Counseling", "Addiction & Substance Abuse Counseling"),

("Mindfulness-Based Therapy", "Mindfulness-Based Therapy"),

("Play Therapy", "Play Therapy"),

("Art Therapy", "Art Therapy"),

("Music Therapy", "Music Therapy"),

("Career Counseling", "Career Counseling"),

("Life Coaching & Personal Development", "Life Coaching & Personal Development"),

("Psychodynamic Therapy", "Psychodynamic Therapy"),

("Acceptance and Commitment Therapy", "Acceptance and Commitment Therapy"),

("Behavioral Therapy", "Behavioral Therapy"),

("Group Therapy", "Group Therapy")

]


class TherapistRegisterForm(BaseRegisterForm):
    # CRITICAL FIX: Add __init__ to dynamically prefix all inherited field IDs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # Apply prefix only if the ID hasn't been explicitly set with a unique prefix
            if 'id' not in field.widget.attrs:
                field.widget.attrs['id'] = f'id_therapist_{name}'
                
    license_number = forms.CharField(required=True)
    specialty = forms.MultipleChoiceField(choices=EXPERTISES, required=True, widget=forms.SelectMultiple(attrs={'class': 'multi-select-specialty'}))
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=True, widget=forms.Select(attrs={'id': 'id_therapist_country', 'class': 'country-select'}))
    province = forms.ChoiceField(choices=[('', 'Select Country First')], required=True, widget=forms.Select(attrs={'id': 'id_therapist_province', 'class': 'province-select'}))
    street = forms.CharField(required=False, help_text="(Optional)", widget=forms.TextInput(attrs={'id': 'id_therapist_street', 'placeholder': 'Street Address'}))
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
            first_name=self.cleaned_data.get("first_name"),
            last_name=self.cleaned_data.get("last_name"),
            license_number=self.cleaned_data["license_number"],
            specialty=", ".join(self.cleaned_data["specialty"]), # Save as comma-separated string
            country=self.cleaned_data["country"],
            province=self.cleaned_data["province"],
            street=self.cleaned_data.get("street"),
            phone_number=self.cleaned_data.get("phone_number"),
        )
        return user