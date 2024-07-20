from django.contrib import admin
from .models import User


@admin.register(User)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "password", "email",)
    list_display_links = ("id",)
    ordering = ["username", "password", "email", ]
