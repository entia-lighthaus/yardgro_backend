from rest_framework import serializers
from .models import Category, Product, ProductRating, Favorite


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']



# Product Rating Serializer
class ProductRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ProductRating
        fields = ['id', 'user', 'rating', 'review', 'created_at']



# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    average_rating = serializers.FloatField(read_only=True)
    ratings = ProductRatingSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock', 'image', 'created_at', 'updated_at',
            'category', 'category_id', 'average_rating', 'ratings'
        ]



# Favorite Serializer
class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'product_id', 'created_at']
