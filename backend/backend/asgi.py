"""
ASGI-конфигурация для проекта backend.

Экспортирует переменную ``application`` — вызываемый объект ASGI-сервера.

Для подробностей:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Указываем модуль настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

application = get_asgi_application()
