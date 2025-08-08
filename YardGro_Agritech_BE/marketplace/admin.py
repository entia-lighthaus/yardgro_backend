from django.contrib import admin
from .models import Category, Product, ProductRating, Favorite

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductRating)
admin.site.register(Favorite)
