from django.contrib import admin
from .models import DailyPost, MoodPost

@admin.register(DailyPost)
class DailyPostAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "text", "created_at")
    search_fields = ("client__user__email", "text")
    list_filter = ("created_at",)

@admin.register(MoodPost)
class MoodPostAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "mood_emoji", "energy_level", "worked_out", "created_at")
    search_fields = ("client__user__email", "mood_emoji", "mood_trigger")
    list_filter = ("created_at",)
