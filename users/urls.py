from django.urls import path
from .views import RegistrationView, LoginView, TokenRefreshCustomView, LogoutView, UserDetailView, UserUpdateView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshCustomView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('<str:username>/', UserDetailView.as_view(), name='user-detail'),
    path('update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
]

