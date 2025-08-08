from rest_framework import serializers
from .models import Category, Product, ProductRating, Favorite

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductRatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')  # Show username, not editable
    
    class Meta:
        model = ProductRating
        fields = ['id', 'product', 'user', 'rating', 'review', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def save(self, **kwargs):
        # Ensure user is set from the request context
        if 'user' not in kwargs and self.context.get('request'):
            kwargs['user'] = self.context['request'].user
        return super().save(**kwargs)

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    ratings = ProductRatingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'image',
            'created_at',
            'updated_at',
            'category',
            'category_id',
            'average_rating',
            'ratings',
        ]
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings.exists():
            return None
        return round(sum(r.rating for r in ratings) / ratings.count(), 2)

class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'product_id', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def save(self, **kwargs):
        # user is set from the request context
        if 'user' not in kwargs and self.context.get('request'):
            kwargs['user'] = self.context['request'].user
        return super().save(**kwargs)