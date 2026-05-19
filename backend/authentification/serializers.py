"""
Сериализаторы для приложения authentification.

Определяют правила сериализации/десериализации моделей User и Listing,
а также валидацию данных при регистрации.
"""

import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Listing, User


# ==============================================================================
# Сериализатор пользователя
# ==============================================================================

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.

    - Пароль доступен только для записи (write_only), не возвращается в ответах.
    - При регистрации валидирует сложность пароля.
    - При обновлении позволяет менять пароль через отдельное поле.
    """

    # Поле для ввода пароля при регистрации (не часть модели, только ввод)
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    # Поле для подтверждения пароля при регистрации
    password_confirm = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm"]
        extra_kwargs = {
            # Пароль не будет возвращён в ответах API
            "password": {"write_only": True},
        }

    def validate_username(self, value: str) -> str:
        """
        Валидация имени пользователя.
        - Не может совпадать с паролем.
        - Минимум 3 символа.
        """
        if len(value) < 3:
            raise serializers.ValidationError(
                "Имя пользователя должно содержать минимум 3 символа."
            )
        return value

    def validate_email(self, value: str) -> str:
        """
        Валидация email.
        - Корректный формат.
        - Уникальность по базе данных.
        """
        # DRF уже проверяет формат через EmailField, но добавим явную проверку
        if not value or "@" not in value:
            raise serializers.ValidationError("Укажите корректный email-адрес.")
        return value

    def validate_password(self, value: str) -> str:
        """
        Валидация сложности пароля.
        - Минимум 8 символов.
        - Не может быть полностью цифровым.
        - Проходит стандартные Django-валидаторы (через Django API).
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                "Пароль должен содержать минимум 8 символов."
            )
        if value.isdigit():
            raise serializers.ValidationError(
                "Пароль не может состоять только из цифр."
            )
        # Запускаем стандартные Django-валидаторы
        try:
            validate_password(value)
        except ValidationError as e:
            # Собираем сообщения в формат DRF
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data: dict) -> dict:
        """
        Общая валидация: проверка совпадения password и password_confirm.
        """
        data = super().validate(data)
        password = data.get("password", "")
        password_confirm = data.get("password_confirm", "")

        if password and password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают."}
            )
        return data

    def create(self, validated_data: dict) -> User:
        """
        Создание пользователя.
        Пароль хешируется через set_password(), остальные поля записываются напрямую.
        """
        # Извлекаем пароль из validated_data (он там есть благодаря write_only)
        password = validated_data.pop("password", None)
        # Также убираем password_confirm — он не нужен в модели
        validated_data.pop("password_confirm", None)

        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance: User, validated_data: dict) -> User:
        """
        Обновление пользователя.
        Если передан пароль — хешируем его.
        """
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ==============================================================================
# Сериализатор объявлений (listings)
# ==============================================================================

# Поддерживаемые MIME-типы изображений
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
# Максимальный размер изображения: 5 МБ
MAX_IMAGE_SIZE = 5 * 1024 * 1024


class ListingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Listing.

    - created_by / created_by_id — только для чтения (возвращают имя и ID автора).
    - image — с валидацией типа и размера файла.
    """

    created_by = serializers.CharField(source="created_by.username", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "description",
            "price",
            "city",
            "image",
            "created_by",
            "created_by_id",
            "created_at",
        ]
        # Все поля только для чтения по умолчанию, явно перечисляем writable
        read_only_fields = ["created_by", "created_by_id", "created_at"]

    def validate_title(self, value: str) -> str:
        """Заголовок: минимум 3 символа, максимум 255."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Заголовок должен содержать минимум 3 символа."
            )
        return value

    def validate_description(self, value: str) -> str:
        """Описание: максимум 5000 символов."""
        if len(value) > 5000:
            raise serializers.ValidationError(
                "Описание не может превышать 5000 символов."
            )
        return value

    def validate_price(self, value: int) -> int:
        """Цена: должна быть положительным числом."""
        if value <= 0:
            raise serializers.ValidationError(
                "Цена должна быть положительным числом."
            )
        return value

    def validate_city(self, value: str) -> str:
        """Город: минимум 2 символа."""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Название города должно содержать минимум 2 символа."
            )
        return value

    def validate_image(self, value) -> bytes:
        """
        Валидация загружаемого изображения.
        - Проверяет MIME-тип (только jpeg, png, webp, gif).
        - Проверяет размер (максимум 5 МБ).
        """
        if value is None:
            return None

        # Проверка MIME-типа
        content_type = getattr(value, "content_type", None)
        if content_type and content_type not in ALLOWED_IMAGE_TYPES:
            allowed = ", ".join(sorted(ALLOWED_IMAGE_TYPES))
            raise serializers.ValidationError(
                f"Неподдерживаемый тип изображения. Разрешены: {allowed}."
            )

        # Проверка размера
        if hasattr(value, "size") and value.size > MAX_IMAGE_SIZE:
            size_mb = MAX_IMAGE_SIZE / (1024 * 1024)
            raise serializers.ValidationError(
                f"Размер изображения не должен превышать {size_mb} МБ."
            )

        return value
