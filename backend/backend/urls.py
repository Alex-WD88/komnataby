from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from .views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', HealthCheckView.as_view(), name='health'),
    path('api/v1/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include("authentification.urls")),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='legacy_token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='legacy_token_refresh'),
    path('', include("authentification.urls")),
]
