#!/usr/bin/env python
"""
Точка входа для Django-управления.

Испольуйте эту утилиту для запуска команд:
    python manage.py runserver      — локальный сервер
    python manage.py migrate        — применение миграций
    python manage.py createsuperuser — создание суперпользователя
    python manage.py test           — запуск тестов
    python manage.py collectstatic  — сборка статики
"""

import os
import sys


def main():
    """Запуск административных задач Django."""
    # Указываем модуль настроек
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Убедитесь, что он установлен "
            "и доступен в переменной окружения PYTHONPATH."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
