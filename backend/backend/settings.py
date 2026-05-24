"""
Настройки Django проекта Komnataby.

Здесь конфигурируются все аспекты приложения:
- Безопасность (SECRET_KEY, CORS, CSRF)
- База данных (PostgreSQL)
- REST Framework и JWT
- drf-spectacular (OpenAPI/Swagger)
- Валидация паролей, статика, медиа
"""

from pathlib import Path
from datetime import timedelta
import os
import secrets

# ==============================================================================
# Базовые пути проекта
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent


def get_bool_env(name: str, default: bool = False) -> bool:
    """
    Преобразует строковое значение переменной окружения в bool.

    Args:
        name: Имя переменной окружения.
        default: Значение по умолчанию, если переменная не задана.

    Returns:
        True если значение '1', 'true', 'yes', 'on' (регистронезависимо),
        иначе — default.
    """
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_list_env(name: str, default: str = "") -> list[str]:
    """
    Преобразует строковое значение переменной окружения в список.

    Значения разделяются запятой. Пустые элементы отфильтровываются.

    Args:
        name: Имя переменной окружения.
        default: Значение по умолчанию.

    Returns:
        Список строк.
    """
    value = os.getenv(name, default)
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


# ==============================================================================
# Безопасность
# ==============================================================================

# Секретный ключ Django.
# ВНИМАНИЕ: никогда не используйте дефолтное значение в продакшене!
# При запуске в продакшене (DEBUG=False) ключ будет сгенерирован автоматически.
# В локальном режиме используется placeholder — обязательно задайте DJANGO_SECRET_KEY.
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    # Placeholder для локальной разработки. При DEBUG=False будет перегенерирован.
    "django-insecure-change-this-in-production-" + secrets.token_hex(16),
)

DEBUG = get_bool_env("DJANGO_DEBUG", True)

# Разрешённые хосты.
# В продакшене обязательно укажите ваши домены через запятую:
#   DJANGO_ALLOWED_HOSTS=komnata.by,www.komnatay
ALLOWED_HOSTS = get_list_env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

# CORS-конфигурация.
# По умолчанию CORS отключён (безопасный default).
# Для локальной разработки раскомментируйте CORS_ALLOWED_ORIGINS в .env.
CORS_ORIGIN_ALLOW_ALL = get_bool_env("DJANGO_CORS_ALLOW_ALL", False)
CORS_ALLOW_CREDENTIALS = get_bool_env("DJANGO_CORS_ALLOW_CREDENTIALS", True)
CORS_ALLOWED_ORIGINS = get_list_env(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    "",  # Пусто по умолчанию — безопасный default
)

# ==============================================================================
# Установленные приложения
# ==============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Внутренние приложения
    "authentification",
    # Сторонние приложения
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
]

# ==============================================================================
# Middleware
# ==============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # CORS middleware должен быть сразу после SessionMiddleware
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

# ==============================================================================
# Шаблоны
# ==============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# ==============================================================================
# База данных (PostgreSQL)
# ==============================================================================

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", "komnata_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "db"),  # По умолчанию — Docker-сервис 'db'
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# ==============================================================================
# Проверка сложности паролей
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},  # Минимум 8 символов
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ==============================================================================
# Международization
# ==============================================================================

LANGUAGE_CODE = "ru-ru"  # Целевая локализация для Беларуси
TIME_ZONE = "Europe/Minsk"
USE_I18N = True
USE_TZ = True

# ==============================================================================
# Статика и медиа
# ==============================================================================

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ==============================================================================
# Primary key field
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==============================================================================
# Django REST Framework
# ==============================================================================

REST_FRAMEWORK = {
    # JWT-аутентификация по умолчанию для всех API-эндпоинтов
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # Стандартные разрешения: аутентифицированные или только чтение
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    # Кастомный обработчик исключений — унифицирует формат ошибок
    "EXCEPTION_HANDLER": "backend.exceptions.api_exception_handler",
    # AutoSchema для drf-spectacular (OpenAPI/Swagger)
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Пагинация по умолчанию для всех списков
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 6,
}

# ==============================================================================
# drf-spectacular (OpenAPI / Swagger)
# ==============================================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Komnataby API",
    "DESCRIPTION": "API для сервиса аренды квартир и комнат komnata.by",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,  # Не включать схему в ответы API
    "COMPONENT_SPLIT_REQUEST": True,
    "CONTACT": {
        "name": "Команда Komnataby",
        "url": "https://komnata.by",
    },
    "LICENSE": {
        "name": "MIT License",
    },
}

# ==============================================================================
# SimpleJWT (JWT-токены)
# ==============================================================================

SIMPLE_JWT = {
    # Access-токен: 60 минут (было 5 — слишком мало для реального использования)
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    # Refresh-токен: 7 дней (было 90 — слишком много, высокий риск кражи)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # Ротация refresh-токенов: каждый use выдаёт новый
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",

    "JTI_CLAIM": "jti",

    # Не используем sliding tokens
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# Пользовательская модель
AUTH_USER_MODEL = "authentification.User"

# ==============================================================================
# Логирование
# ==============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
