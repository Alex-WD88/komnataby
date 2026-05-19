"""
URL-конфигурация корневого проекта.

Содержит:
- Админка Django
- Health check
- JWT-токены (obtain pair, refresh)
- Эндпоинты приложения authentification
- OpenAPI/Swagger документация
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import HealthCheckView
from authentification.views import CustomTokenObtainPairView

urlpatterns = [
    # Django админ-панель
    path("admin/", admin.site.urls),

    # Проверка здоровья сервиса
    path("api/v1/health/", HealthCheckView.as_view(), name="health"),

    # JWT-аутентификация (SimpleJWT)
    path("api/v1/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),

    # Эндпоинты приложения authentification
    path("api/v1/", include("authentification.urls")),

    # OpenAPI/Swagger документация
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
]

# При DEBUG=True раздаём медиафайлы напрямую
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
