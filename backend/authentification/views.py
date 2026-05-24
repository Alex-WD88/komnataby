"""
Views приложения authentification.

Содержит эндпоинты для:
- Проверки здоровья сервиса (health check)
- Аутентификации (login, register, logout, token refresh)
- Управления объявлениями (CRUD listings)
"""

import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions

from .models import Listing
from .serializers import (
    UserSerializer,
    ListingSerializer,
)

# Логгер для приложения authentification
logger = logging.getLogger(__name__)

# ==============================================================================
# Health check — проверка доступности сервиса
# ==============================================================================

class HealthCheckView(APIView):
    """
    Эндпоинт проверки доступности API.
    Не требует аутентификации.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiResponse(description="HealthCheckResponse")})
    def get(self, request):
        return Response({
            "ok": True,
            "data": {
                "status": "ok",
                "service": "komnataby-backend",
            },
        })


# ==============================================================================
# Кастомный TokenObtainPairView — унифицированный формат ответа
# ==============================================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Стандартный эндпоинт SimpleJWT для получения пары токенов.

    Переопределяет формат ответа для единообразия:
    - Успех: {"ok": True, "data": {"access": "...", "refresh": "..."}}
    - Ошибка: {"ok": False, "error": {...}}

    Rate limiting: максимум 5 попыток в минуту на IP-адрес.
    """

    permission_classes = [AllowAny]

    @ratelimit(key="ip", rate="5/m")
    def post(self, request, *args, **kwargs):
        # Проверяем, не превышен ли лимит
        was_limited = getattr(request, "limited", False)
        if was_limited:
            return Response({
                "ok": False,
                "error": {
                    "code": "rate_limited",
                    "message": "Слишком много попыток. Подождите минуту.",
                    "details": {},
                },
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return Response({
                "ok": True,
                "data": response.data,
            })
        # При ошибке (неверные учётные данные) возвращаем формат ошибки
        return Response({
            "ok": False,
            "error": {
                "code": "authentication_error",
                "message": response.data.get("detail", "Неверные учётные данные."),
                "details": response.data,
            },
        }, status=response.status_code)


# ==============================================================================
# Регистрация пользователя
# ==============================================================================

class RegisterView(APIView):
    """
    Эндпоинт регистрации нового пользователя.

    - Принимает username, email, password, password_confirm.
    - Валидирует все поля через UserSerializer.
    - При конфликте уникальности (дубликат username/email) возвращает понятную ошибку.

    Rate limiting: максимум 3 регистрации в минуту на IP-адрес.
    """

    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    @ratelimit(key="ip", rate="3/m")
    def post(self, request):
        # Проверяем, не превышен ли лимит
        was_limited = getattr(request, "limited", False)
        if was_limited:
            return Response({
                "ok": False,
                "error": {
                    "code": "rate_limited",
                    "message": "Слишком много попыток регистрации. Подождите минуту.",
                    "details": {},
                },
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # После регистрации автоматически выдаём JWT-токены
            refresh = RefreshToken.for_user(user)

            return Response({
                "ok": True,
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as exc:
            # Ловим дубликаты username/email на уровне БД
            logger.warning("Регистрация: дубликат — %s", exc)
            return Response({
                "ok": False,
                "error": {
                    "code": "integrity_error",
                    "message": "Пользователь с таким именем или email уже существует.",
                    "details": {},
                },
            }, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# Выход (logout) — блокировка refresh-токена
# ==============================================================================

class LogoutView(APIView):
    """
    Эндпоинт выхода. Блокирует (blacklist) переданный refresh-токен,
    после чего он больше не может использоваться для получения новых access-токенов.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={205: OpenApiResponse(description="LogoutSuccess"), 400: OpenApiResponse(description="Error")})
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({
                    "ok": False,
                    "error": {
                        "code": "missing_refresh_token",
                        "message": "Не передан refresh_token.",
                        "details": {},
                    },
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  # Блокируем токен

            return Response({
                "ok": True,
                "data": {"message": "Вы успешно вышли из системы."},
            }, status=status.HTTP_205_RESET_CONTENT)

        except Exception as exc:
            logger.error("Logout ошибка: %s", exc)
            return Response({
                "ok": False,
                "error": {
                    "code": "invalid_refresh_token",
                    "message": "Refresh-токен недействителен или уже заблокирован.",
                    "details": {},
                },
            }, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# Защищённая страница (dashboard)
# ==============================================================================

class HomeView(APIView):
    """
    Защищённый эндпоинт — проверяет валидность JWT и возвращает приветствие.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse(description="HomeResponse")})
    def get(self, request):
        content = {
            "message": f"Добро пожаловать, {request.user.username}!",
            "user_id": request.user.id,
        }
        return Response({"ok": True, "data": content})


# ==============================================================================
# Пагинация для объявлений
# ==============================================================================

class ListingPagination(PageNumberPagination):
    """
    Пагинация для списка объявлений.
    - page_size: 6 записей на страницу.
    - page_size_query_param: клиент может запросить свой размер через ?page_size=N.
    - max_page_size: ограничение — 50 записей.
    """
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 50


# ==============================================================================
# Разрешение: владелец или только чтение для других
# ==============================================================================

class IsListingOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование/удаление только создателю объявления.
    Для всех остальных — только чтение (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем
        if request.method in generics.SafeMethods:
            return True
        # Запись только автору
        return request.user.is_authenticated and obj.created_by_id == request.user.id


# ==============================================================================
# Список + создание объявлений
# ==============================================================================

class ListingListCreateView(generics.ListCreateAPIView):
    """
    GET  — список объявлений с фильтрацией и пагинацией.
    POST — создание нового объявления (только для аутентифицированных).
    """

    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Listing.objects.select_related("created_by").all()
    pagination_class = ListingPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """
        Фильтрация и сортировка списка объявлений.

        Параметры запроса:
        - search: поиск по заголовку (подстрока, регистронезависимо)
        - city: фильтр по городу (подстрока)
        - min_price: минимальная цена
        - max_price: максимальная цена
        - ordering: сортировка (date_desc, date_asc, price_asc, price_desc)
        """
        queryset = super().get_queryset()

        search = self.request.query_params.get("search")
        city = self.request.query_params.get("city")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        ordering = self.request.query_params.get("ordering")

        if search:
            queryset = queryset.filter(title__icontains=search)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        ordering_map = {
            "price_asc": "price",
            "price_desc": "-price",
            "date_asc": "created_at",
            "date_desc": "-created_at",
        }
        queryset = queryset.order_by(ordering_map.get(ordering, "-created_at"))
        return queryset

    def perform_create(self, serializer):
        """
        При создании объявления привязываем текущего пользователя как автора.
        """
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Переопределяем list() для унифицированного формата ответа:
        {"ok": True, "data": [...], "count": N, "next": ..., "previous": ...}
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "ok": True,
                "data": serializer.data,
            })
        serializer = self.get_serializer(queryset, many=True)
        return Response({"ok": True, "data": serializer.data})

    def create(self, request, *args, **kwargs):
        """
        Переопределяем create() для унифицированного формата ответа.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "ok": True,
            "data": serializer.data,
        }, status=status.HTTP_201_CREATED)


# ==============================================================================
# Детали объявления: просмотр, обновление, удаление
# ==============================================================================

class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    — просмотр одного объявления
    PATCH  — частичное обновление (только автор)
    PUT    — полное обновление (только автор)
    DELETE — удаление (только автор)
    """

    serializer_class = ListingSerializer
    queryset = Listing.objects.select_related("created_by").all()
    permission_classes = [IsListingOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"ok": True, "data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"ok": True, "data": serializer.data})

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "ok": True,
            "data": {"message": "Объявление успешно удалено."},
        })
