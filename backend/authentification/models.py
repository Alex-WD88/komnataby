"""
Модели приложения authentification.

Содержит:
- User: кастомная модель пользователя (наследует AbstractUser).
- Listing: объявление (аренда комнаты/квартиры).
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


# ==============================================================================
# Кастомная модель пользователя
# ==============================================================================

class User(AbstractUser):
    """
    Пользователь системы.

    Наследует все поля AbstractUser (username, password, is_active, etc.)
    и добавляет:
    - email: обязательный уникальный email.
    - USERNAME_FIELD = 'username': поле для входа — имя пользователя.
    - REQUIRED_FIELDS = ['email']: email обязателен при создании через createsuperuser.
    """

    username = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Имя пользователя",
        help_text="Уникальное имя для входа в систему.",
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name="Email",
        help_text="Уникальный email-адрес.",
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Пароль",
    )

    # Поле, используемое для аутентификации (вместо default 'username')
    USERNAME_FIELD = "username"
    # Поля, обязательные при создании через createsuperuser
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username


# ==============================================================================
# Модель объявления
# ==============================================================================

class Listing(models.Model):
    """
    Объявление об аренде комнаты или квартиры.

    Связано с пользователем (created_by) — один-to-many.
    При удалении пользователя все его объявления удаляются (CASCADE).
    """

    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок",
        help_text="Краткое описание объявления.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Подробное описание объявления (необязательно).",
    )
    price = models.PositiveIntegerField(
        verbose_name="Цена",
        help_text="Стоимость аренды (в валюте, указанной на сайте).",
    )
    city = models.CharField(
        max_length=128,
        verbose_name="Город",
        help_text="Город, где находится объект.",
    )
    image = models.ImageField(
        upload_to="listings/",
        blank=True,
        null=True,
        verbose_name="Фотография",
        help_text="Фото объекта (необязательно).",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="listings",
        verbose_name="Автор",
        help_text="Пользователь, создавший объявление.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]  # Новые первыми

    def __str__(self):
        return self.title
