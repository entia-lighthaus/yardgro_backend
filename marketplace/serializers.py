from rest_framework import serializers
from .models import Category, Product, ProductRating, Favorite


# Serializer for Category Models
# This serializer handles the creation and validation of categories.
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']



# Serializer for Product Ratings
# This serializer handles the creation and validation of product ratings.
# It ensures that a user can only rate a product once.
class ProductRatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    #product = serializers.ReadOnlyField(source='product.id')

    class Meta:
        model = ProductRating
        fields = ['id', 'user', 'product', 'rating', 'review', 'created_at']
        read_only_fields = ['id', 'user', 'product', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        product = self.context['product'] if 'product' in self.context else validated_data.get('product')
        rating = validated_data.get('rating')
        review = validated_data.get('review', '')

        # Prevent duplicate ratings for the same user and product
        existing = ProductRating.objects.filter(user=user, product=product).first()
        if existing:
            # Update the existing rating
            existing.rating = rating
            existing.review = review
            existing.save()
            return existing
        return ProductRating.objects.create(user=user, product=product, rating=rating, review=review)
    



# Serializer for Product Models
# This serializer handles the creation and validation of products.
# It includes nested serializers for categories and product ratings.
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



# Serializer for Favorite Model
# This serializer handles the creation and validation of favorite products for users.
# It handles the error when someone tries to save the same product twice, with a specific message.
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

    
    def validate(self, attrs):
        user = self.context['request'].user
        product = attrs.get('product')
        if Favorite.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError({"detail": "your brilliant choice has been saved by you before"}) # This is a specific error message for duplicate favorites
        return attrs

    def save(self, **kwargs):
        if 'user' not in kwargs and self.context.get('request'):
            kwargs['user'] = self.context['request'].user
        return super().save(**kwargs)