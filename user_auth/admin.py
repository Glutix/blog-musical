from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "birth_date", "is_author", "created_at")
    list_filter = ("is_author", "birth_date", "created_at")
    search_fields = ("user__username", "bio", "web_site")
    readonly_fields = ("created_at",)
