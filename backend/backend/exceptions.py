"""
Кастомный обработчик исключений для Django REST Framework.

Унифицирует формат всех ошибок API:
{
    "ok": false,
    "error": {
        "code": "http_400",
        "message": "Описание ошибки",
        "details": { ... }
    }
}

Для 500 ошибок возвращается:
{
    "ok": false,
    "error": {
        "code": "server_error",
        "message": "Unexpected server error.",
        "details": {}
    }
}
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """
    Обработчик исключений DRF.

    Args:
        exc: Исключение, которое было выброшено.
        context: Словарь с контекстом запроса (request, view, args, kwargs).

    Returns:
        Response с унифицированным форматом ошибки.
        None, если исключение не должно быть обработано (например, 404).
    """
    # Сначала вызываем стандартный обработчик DRF
    response = exception_handler(exc, context)

    # Если response == None — исключение не было обработано DRF
    # (например, Django 404). Возвращаем наш формат.
    if response is None:
        return Response(
            {
                "ok": False,
                "error": {
                    "code": "server_error",
                    "message": "Неожиданная ошибка сервера.",
                    "details": {},
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Парсим данные ответа и форматируем в единый стиль
    if isinstance(response.data, dict):
        details = response.data
        message = details.get("detail")
        if isinstance(message, list):
            message = message[0]
        if not message:
            message = "Запрос не выполнен."
    else:
        details = {"detail": response.data}
        message = "Запрос не выполнен."

    # Возвращаем унифицированный формат ошибки
    response.data = {
        "ok": False,
        "error": {
            "code": f"http_{response.status_code}",
            "message": str(message),
            "details": details,
        },
    }
    return response
