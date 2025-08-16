from rest_framework import serializers
from .models import UserPreference, Spin, SpinItem, Basket, Badge, UserBadge


# User Preference Serializer
# This serializer handles the user preferences for spins.
# It allows users to set their preferences for product categories, price ranges, and other criteria.
class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = '__all__'


# Spin Serializer
# This serializer handles the spin data for the roulette feature.
# It allows users to view and manage their spins, including budget, preferences, and selected items.
class SpinSerializer(serializers.ModelSerializer):
    preferences = UserPreferenceSerializer(read_only=True)
    preferences_snapshot = serializers.JSONField(read_only=True)
    class Meta:
        model = Spin
        fields = '__all__'

# Create Spin Serializer
# This serializer is used to create a new spin with a budget and currency.
class CreateSpinSerializer(serializers.Serializer):
    budget = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1000)
    currency = serializers.CharField(max_length=3, default='NGN')


# Spin Item Serializer
# This serializer handles the individual items within a spin.
# It allows users to view and manage the products selected in their spins.
class SpinItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpinItem
        fields = '__all__'


# Basket Serializer
# This serializer handles the user's shopping basket, which can contain multiple SpinItems.
# It allows users to view and manage the items they have selected for checkout.
class BasketSerializer(serializers.ModelSerializer):
    items = SpinItemSerializer(many=True, read_only=True)
    class Meta:
        model = Basket
        fields = '__all__'


# Badge Serializer
# This serializer handles the badge data for users.
# It allows users to view and manage the badges they have earned.
class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'


# User Badge Serializer
# This serializer links users to their badges.
# It allows users to view the badges they have earned and the details of each badge.
class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    class Meta:
        model = UserBadge
        fields = '__all__'