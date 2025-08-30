from django.urls import path
from .views import (
    UserPreferenceView, SpinListCreateView, SpinDetailView, SpinCheckoutView,
    SpinItemListView, SpinItemUpdateView, SpinItemSelectView, SelectedSpinItemListView, AddSelectedItemsToBasketView,AddAllSpinItemsToBasketView, BasketListCreateView, BadgeListView, UserBadgeListView,
    SpinHistoryView, start_item_selection
)

urlpatterns = [
    path('preferences/', UserPreferenceView.as_view(), name='user-preferences'),
    path('spins/', SpinListCreateView.as_view(), name='spin-list-create'),
    path('spin/<uuid:pk>/', SpinDetailView.as_view(), name='spin-detail'),
    path('spins/<uuid:spin_id>/items/', SpinItemListView.as_view(), name='spin-item-list'),
    path('spin/items/<uuid:pk>/', SpinItemUpdateView.as_view(), name='spin-item-update'),
    path('spins/<uuid:spin_id>/checkout/', SpinCheckoutView.as_view(), name='spin-checkout'),
    path('spins/history/', SpinHistoryView.as_view(), name='spin-history'),
    path('spins/<uuid:spin_id>/start-selection/', start_item_selection, name='start-item-selection'),
    path('spins/<uuid:spin_id>/items/<uuid:item_id>/select/',SpinItemSelectView.as_view(), name='spin-item-select'), # Select or deselect an item in a specific spin
    path('spins/<uuid:spin_id>/selected-items/', SelectedSpinItemListView.as_view(), name='selected-spin-item-list'), # List all selected items in a specific spin
    path('spin/<uuid:spin_id>/add-to-basket/', AddSelectedItemsToBasketView.as_view(), name='add-selected-to-basket'), # Add selected items to cart
    path('spins/<uuid:spin_id>/add-all-to-basket/', AddAllSpinItemsToBasketView.as_view(), name='add-all-to-basket'), # Add all items in a spin to cart
    path('baskets/', BasketListCreateView.as_view(), name='basket-list-create'),
    path('badges/', BadgeListView.as_view(), name='badge-list'),
    path('user-badges/', UserBadgeListView.as_view(), name='user-badge-list'),
]

