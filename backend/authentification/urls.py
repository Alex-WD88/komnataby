"""
URL-конфигурация приложения authentification.

Все эндпоинты приложения:
- home/        — защищённая страница (dashboard)
- logout/      — выход (блокировка refresh-токена)
- register/    — регистрация нового пользователя
- listings/    — CRUD-операции с объявлениями
"""

from django.urls import path
from . import views

urlpatterns = [
    # Защищённая страница
    path("home/", views.HomeView.as_view(), name="home"),
    # Выход
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # Регистрация
    path("register/", views.RegisterView.as_view(), name="register"),
    # Объявления
    path("listings/", views.ListingListCreateView.as_view(), name="listings"),
    path("listings/<int:pk>/", views.ListingDetailView.as_view(), name="listing-detail"),
]
