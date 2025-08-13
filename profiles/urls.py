from django.urls import path
from . import views

urlpatterns = [
    # Example endpoints for profiles
    path('', views.ProfileListView.as_view(), name='profile-list'),  # List all profiles
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),  # View/update a profile
    # Add more endpoints as needed
]
