from django.urls import path
from .views import (
    CategoryListCreateAPIView, CategoryRetrieveUpdateDestroyAPIView,
    ProductListCreateAPIView, ProductRetrieveUpdateDestroyAPIView, ProductRatingCreateUpdateAPIView, 
    FavoriteListView, FavoriteCreateView, FavoriteDeleteView, 
    ProductRatingListView, ProductRatingDetailView
)


urlpatterns = [
    # Categories
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-detail'),

    # Products
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-detail'),

    # Ratings
    path('products/rate/', ProductRatingCreateUpdateAPIView.as_view(), name='product-rate'),
    path('products/ratings/', ProductRatingListView.as_view(), name='product-rating-list'),
    path('products/ratings/<int:pk>/', ProductRatingDetailView.as_view(), name='product-rating-detail'),

    # Favorites
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/add/', FavoriteCreateView.as_view(), name='favorite-add'),
    path('favorites/<int:pk>/', FavoriteDeleteView.as_view(), name='favorite-delete'),
]


