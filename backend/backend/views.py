"""
Вспомогательные views корневого приложения backend.

Содержит health-check эндпоинт для проверки доступности API.
"""

from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.types import OpenApiTypes


class HealthCheckView(APIView):
    """
    Эндпоинт проверки доступности API.

    GET /api/v1/health/ -> {"ok": true, "data": {"status": "ok", "service": "komnataby-backend"}}

    Не требует аутентификации.
    Используется для healthcheck в Docker и мониторинга.
    """

    authentication_classes = []
    permission_classes = []

    @extend_schema(
        responses={
            200: OpenApiResponse(response=OpenApiTypes.OBJECT, description="API is healthy"),
        }
    )
    def get(self, request):
        return Response({
            "ok": True,
            "data": {
                "status": "ok",
                "service": "komnataby-backend",
            },
        })
