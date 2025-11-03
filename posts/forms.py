# forms.py
from django import forms
from .models import DailyPost, MoodPost

class DailyPostForm(forms.ModelForm):
    class Meta:
        model = DailyPost
        fields = ['text', 'commentary']

class MoodPostForm(forms.ModelForm):
    MOOD_CHOICES = [
        ('happy', '😊 Happy'),
        ('neutral', '😐 Neutral'),
        ('sad', '😔 Sad'),
    ]

    mood_emoji = forms.ChoiceField(choices=MOOD_CHOICES, widget=forms.RadioSelect)
    energy_level = forms.IntegerField(min_value=1, max_value=5)
    mood_trigger = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    worked_out = forms.BooleanField(required=False)

    class Meta:
        model = MoodPost
        fields = ['mood_emoji', 'energy_level', 'mood_trigger', 'worked_out']
