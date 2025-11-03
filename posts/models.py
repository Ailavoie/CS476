# models.py
from django.db import models
from ckeditor.fields import RichTextField
from accounts.models import ClientProfile


class BasePost(models.Model):  # Abstract base class for posts
    POST_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('mood', 'Mood'),
    ]

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    therapist_comment_notification = models.BooleanField(default=False)
    client_post_notification = models.BooleanField(default=True)
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
    commentary = models.TextField(blank=True, null=True)
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
