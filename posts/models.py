# models.py
from django.db import models
from ckeditor.fields import RichTextField
from accounts.models import ClientProfile, TherapistProfile

# Subject of observer pattern
# Abstract base class for DailyPost and MoodPost models
class BasePost(models.Model):  
    POST_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('mood', 'Mood'),
    ]

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    therapist_comment_notification = models.BooleanField(default=False) #Used by Concrete Observer in Observer pattern
    post_type = models.CharField(
        max_length=10,
        choices=POST_TYPE_CHOICES
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.post_type.capitalize()} post by {self.client.user.email} on {self.created_at.strftime('%Y-%m-%d')}"


class DailyPost(BasePost): # Daily journal entry)
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="daily_posts"
    )
    text = RichTextField()
    post_type = models.CharField(max_length=20, default='daily', editable=False)


    def save(self, *args, **kwargs):
        self.post_type = 'daily'
        super().save(*args, **kwargs)


class MoodPost(BasePost): # Mood journal entry
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="mood_posts"
    )
    mood_emoji = models.CharField(max_length=10)
    energy_level = models.PositiveSmallIntegerField()
    worked_out = models.BooleanField(default=False)
    mood_trigger = models.TextField()
    post_type = models.CharField(max_length=20, default='mood', editable=False)


    def save(self, *args, **kwargs):
        self.post_type = 'mood'
        super().save(*args, **kwargs)

class Comment(models.Model):
    therapist = models.ForeignKey(
        TherapistProfile,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    daily_post = models.ForeignKey(
        "DailyPost",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments"
    )
    mood_post = models.ForeignKey(
        "MoodPost",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        target = self.daily_post or self.mood_post
        return f"Comment by {self.therapist.user.email} on {target}"