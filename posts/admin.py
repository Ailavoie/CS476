from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "text", "created_at")
    search_fields = ("client__user__email", "text")
    list_filter = ("created_at",)
