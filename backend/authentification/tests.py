"""
Тесты для приложения authentification.

Категории тестов:
1. Модели — User и Listing
2. Сериализаторы — валидация пароля, email, изображений
3. Views — регистрация, логин, listings CRUD
"""

import io
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Listing
from .serializers import UserSerializer, ListingSerializer

User = get_user_model()


# ==============================================================================
# Тесты моделей
# ==============================================================================

class UserTestCase(TestCase):
    """Тесты модели User."""

    def setUp(self):
        """Создаём тестового пользователя."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_user_str(self):
        """Метод __str__ возвращает username."""
        self.assertEqual(str(self.user), "testuser")

    def test_user_email_unique(self):
        """Email должен быть уникальным."""
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="testuser2",
                email="test@example.com",
                password="testpass123",
            )


class ListingTestCase(TestCase):
    """Тесты модели Listing."""

    def setUp(self):
        """Создаём тестового пользователя и объявление."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.listing = Listing.objects.create(
            title="Квартира в Минске",
            description="Уютная двухкомнатная квартира",
            price=500,
            city="Минск",
            created_by=self.user,
        )

    def test_listing_str(self):
        """Метод __str__ возвращает заголовок."""
        self.assertEqual(str(self.listing), "Квартира в Минске")

    def test_listing_created_by_cascade(self):
        """При удалении пользователя объявления удаляются."""
        user_id = self.user.id
        self.user.delete()
        self.assertFalse(
            Listing.objects.filter(id=user_id).exists(),
            "Объявление должно быть удалено при CASCADE",
        )


# ==============================================================================
# Тесты сериализаторов
# ==============================================================================

class UserSerializerTestCase(TestCase):
    """Тесты сериализатора UserSerializer."""

    def test_valid_registration(self):
        """Валидная регистрация проходит успешно."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpass1",
            "password_confirm": "strongpass1",
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_mismatch(self):
        """Разные пароли — ошибка валидации."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpass1",
            "password_confirm": "differentpass",
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_short_password(self):
        """Слишком короткий пароль — ошибка."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "123",
            "password_confirm": "123",
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_numeric_password(self):
        """Пароль из одних цифр — ошибка."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "12345678",
            "password_confirm": "12345678",
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_short_username(self):
        """Слишком короткое имя пользователя — ошибка."""
        data = {
            "username": "ab",
            "email": "new@example.com",
            "password": "strongpass1",
            "password_confirm": "strongpass1",
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_password_not_in_output(self):
        """Пароль не должен возвращаться в сериализованных данных."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="secret123",
        )
        serializer = UserSerializer(user)
        self.assertNotIn("password", serializer.data)


class ListingSerializerTestCase(TestCase):
    """Тесты сериализатора ListingSerializer."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_valid_listing(self):
        """Валидное объявление проходит проверку."""
        data = {
            "title": "Квартира",
            "description": "Описание",
            "price": 500,
            "city": "Минск",
        }
        serializer = ListingSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_price(self):
        """Отрицательная цена — ошибка."""
        data = {
            "title": "Квартира",
            "description": "Описание",
            "price": -100,
            "city": "Минск",
        }
        serializer = ListingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_invalid_title(self):
        """Слишком короткий заголовок — ошибка."""
        data = {
            "title": "а",
            "description": "Описание",
            "price": 500,
            "city": "Минск",
        }
        serializer = ListingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)


# ==============================================================================
# Тесты API-эндпоинтов
# ==============================================================================

class AuthAPITestCase(APITestCase):
    """Тесты API-эндпоинтов аутентификации."""

    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        """Регистрация создаёт пользователя и возвращает токены."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpass1",
            "password_confirm": "strongpass1",
        }
        response = self.client.post("/api/v1/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get("ok"))
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])

        # Проверяем, что пользователь создан в БД
        self.assertTrue(
            User.objects.filter(username="newuser").exists()
        )

    def test_register_password_mismatch(self):
        """Разные пароли при регистрации — ошибка."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "pass1234",
            "password_confirm": "pass5678",
        }
        response = self.client.post("/api/v1/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get("ok"))

    def test_register_short_password(self):
        """Слишком короткий пароль — ошибка."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "123",
            "password_confirm": "123",
        }
        response = self.client.post("/api/v1/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        """Логин возвращает токены."""
        User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="loginpass1",
        )
        data = {"username": "loginuser", "password": "loginpass1"}
        response = self.client.post("/api/v1/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("ok"))
        self.assertIn("access", response.data["data"])

    def test_login_invalid_credentials(self):
        """Неверные учётные данные — ошибка."""
        User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="loginpass1",
        )
        data = {"username": "loginuser", "password": "wrongpass"}
        response = self.client.post("/api/v1/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data.get("ok"))

    def test_home_requires_auth(self):
        """Эндпоинт /home/ требует аутентификации."""
        response = self.client.get("/api/v1/home/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_home_returns_data_for_authenticated(self):
        """Аутентифицированный пользователь получает данные с /home/."""
        user = User.objects.create_user(
            username="dashuser",
            email="dash@example.com",
            password="dashpass1",
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/home/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("ok"))
        self.assertIn("message", response.data["data"])

    def test_logout(self):
        """Logout блокирует refresh-токен."""
        user = User.objects.create_user(
            username="logoutuser",
            email="logout@example.com",
            password="logoutpass1",
        )
        refresh = RefreshToken.for_user(user)
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/v1/logout/",
            {"refresh_token": str(refresh)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertTrue(response.data.get("ok"))

    def test_health_check(self):
        """Health check доступен без аутентификации."""
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("ok"))


class ListingAPITestCase(APITestCase):
    """Тесты API-эндпоинтов объявлений."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="listinguser",
            email="listing@example.com",
            password="listingpass1",
        )
        self.listing = Listing.objects.create(
            title="Тестовое объявление",
            description="Описание объявления",
            price=500,
            city="Минск",
            created_by=self.user,
        )

    def test_listings_list_requires_auth(self):
        """Список объявлений доступен всем (без аутентификации)."""
        # listingListCreateView использует IsAuthenticatedOrReadOnly
        # GET без аутентификации должен работать
        response = self.client.get("/api/v1/listings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listings_create_requires_auth(self):
        """Создание объявления требует аутентификации."""
        data = {
            "title": "Новое объявление",
            "description": "Описание",
            "price": 600,
            "city": "Гомель",
        }
        response = self.client.post("/api/v1/listings/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listings_create(self):
        """Аутентифицированный пользователь создаёт объявление."""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Новое объявление",
            "description": "Описание",
            "price": 600,
            "city": "Гомель",
        }
        response = self.client.post("/api/v1/listings/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get("ok"))
        self.assertEqual(Listing.objects.count(), 2)

    def test_listing_detail_retrieve(self):
        """Просмотр одного объявления доступно всем."""
        response = self.client.get(f"/api/v1/listings/{self.listing.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("ok"))

    def test_listing_update_owner(self):
        """Автор может обновить своё объявление."""
        self.client.force_authenticate(user=self.user)
        data = {"title": "Обновлённый заголовок"}
        response = self.client.patch(
            f"/api/v1/listings/{self.listing.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "Обновлённый заголовок")

    def test_listing_update_non_owner_fails(self):
        """Неавтор не может обновить чужое объявление."""
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass1",
        )
        self.client.force_authenticate(user=other_user)
        data = {"title": "Хак"}
        response = self.client.patch(
            f"/api/v1/listings/{self.listing.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listing_delete_owner(self):
        """Автор может удалить своё объявление."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/v1/listings/{self.listing.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Listing.objects.filter(id=self.listing.id).exists()
        )

    def test_listing_filter_by_city(self):
        """Фильтрация по городу работает."""
        Listing.objects.create(
            title="Гомельская квартира",
            price=400,
            city="Гомель",
            created_by=self.user,
        )
        response = self.client.get("/api/v1/listings/?city=Минск")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_listing_filter_by_price_range(self):
        """Фильтрация по цене работает."""
        Listing.objects.create(
            title="Дешёвое",
            price=200,
            city="Минск",
            created_by=self.user,
        )
        response = self.client.get("/api/v1/listings/?min_price=300&max_price=600")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Только одно объявление в диапазоне 300-600
        self.assertEqual(len(response.data["data"]), 1)


# ==============================================================================
# Тесты exception handler
# ==============================================================================

class ExceptionHandlerTestCase(TestCase):
    """Тесты кастомного обработчика исключений."""

    def setUp(self):
        self.client = APIClient()

    def test_404_returns_unified_format(self):
        """Эндпоинт 404 возвращает унифицированный формат ошибки."""
        response = self.client.get("/api/v1/nonexistent/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data.get("ok"))
        self.assertIn("error", response.data)
        self.assertIn("message", response.data["error"])
