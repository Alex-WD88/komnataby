"""
Админ-панель для приложения authentification.

Регистрирует модели User и Listing в Django admin с настроенными
колонками, фильтрами и поиском.
"""

from django.contrib import admin
from .models import Listing, User


# ==============================================================================
# Админка для пользователей
# ==============================================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Настройки отображения пользователей в админке.
    - list_display: колонки таблицы.
    - list_display_links: кликабельные колонки (переход к редактированию).
    - list_filter: фильтры сбоку.
    - search_fields: поиск по полям.
    - ordering: сортировка по умолчанию.
    """
    list_display = ("id", "username", "email", "is_active", "is_staff", "date_joined")
    list_display_links = ("id", "username")
    list_filter = ("is_active", "is_staff", "is_superuser", "date_joined")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)
    # Пароль НЕ выводим в списке — это небезопасно и бессмысленно (хеш)


# ==============================================================================
# Админка для объявлений
# ==============================================================================

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """
    Настройки отображения объявлений в админке.
    """
    list_display = ("id", "title", "price", "city", "created_by", "created_at")
    list_display_links = ("id", "title")
    list_filter = ("city", "created_at")
    search_fields = ("title", "city", "created_by__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
