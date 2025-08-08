from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductRating, Favorite

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'image_tag', 'created_at')
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: contain;" />', obj.image.url)
        return "(No Image)"
    image_tag.short_description = 'Image'

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductRating)
admin.site.register(Favorite)
