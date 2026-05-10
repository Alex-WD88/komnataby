from django.urls import path
from .views import *

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('listings/', ListingListCreateView.as_view(), name='listings'),
    path('listings/<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
]
