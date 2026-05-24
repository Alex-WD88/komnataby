# ==============================================================================
# Многоэтапный Dockerfile для Django-бэкенда
# ==============================================================================
# Этап 1: build — установка зависимостей
# Этап 2: runtime — финальный образ с приложением
# ==============================================================================

# ---------- Этап 1: сборка зависимостей ----------
FROM python:3.12-slim AS builder

# Создаём рабочую директорию
WORKDIR /app

# Копируем только requirements для кэширования слоёв
COPY requirements.txt .

# Устанавливаем зависимости в изолированное окружение
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Этап 2: финальный образ ----------
FROM python:3.12-slim

# Метаданные
LABEL maintainer="komnataby-team"
LABEL description="Django backend for Komnataby"

# Переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Безопасность: создаём непривилегированного пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Рабочая директория
WORKDIR /app

# Копируем зависимости из builder-этапа
COPY --from=builder /app/.venv /app/.venv

# Копируем содержимое директории backend в /app, сохраняя структуру
COPY . /app

# Создаём директории для статики и медиа
RUN mkdir -p /app/staticfiles /app/media && chown -R appuser:appuser /app

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт
EXPOSE 8000

# Healthcheck — проверяем доступность API
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/')" || exit 1

# Запуск через gunicorn (wsgi.py находится в /app/backend/wsgi.py)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--chdir", "/app/backend", "wsgi:application"]
