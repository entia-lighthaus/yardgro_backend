from django.urls import path
from .views import OrderListCreateView, OrderDetailView


# URL patterns for order management
urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]
