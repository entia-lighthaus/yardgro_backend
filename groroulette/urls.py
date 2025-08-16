from django.urls import path
from .views import (
    UserPreferenceView, SpinListCreateView, SpinDetailView,
    SpinItemListView, BasketListCreateView, BadgeListView, UserBadgeListView,
    SpinHistoryView, start_item_selection
)

urlpatterns = [
    path('preferences/', UserPreferenceView.as_view(), name='user-preferences'),
    path('spins/', SpinListCreateView.as_view(), name='spin-list-create'),
    path('spins/<uuid:pk>/', SpinDetailView.as_view(), name='spin-detail'),
    path('spins/<uuid:spin_id>/items/', SpinItemListView.as_view(), name='spin-item-list'),
    path('spins/history/', SpinHistoryView.as_view(), name='spin-history'),
    path('spins/<uuid:spin_id>/start-selection/', start_item_selection, name='start-item-selection'),
    path('baskets/', BasketListCreateView.as_view(), name='basket-list-create'),
    path('badges/', BadgeListView.as_view(), name='badge-list'),
    path('user-badges/', UserBadgeListView.as_view(), name='user-badge-list'),
]