from django.db import models
from accounts.models import ClientProfile

class Post(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="posts")
    text = models.TextField()
    commentary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    therapist_comment_notification = models.BooleanField(default=False)
    client_post_notification = models.BooleanField(default=True)


    def __str__(self):
        return f"Post by {self.client.user.email} on {self.created_at.strftime('%Y-%m-%d')}"
