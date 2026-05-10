from django.contrib import admin
from .models import Listing, User


@admin.register(User)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "password", "email",)
    list_display_links = ("id",)
    ordering = ["username", "password", "email", ]


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "city", "created_by", "created_at")
    list_filter = ("city", "created_at")
    search_fields = ("title", "city", "created_by__username")
