from rest_framework import serializers
from .models import UserPreference, Spin, SpinItem, Badge, UserBadge
from orders.models import Basket, BasketItem

# User Preference Serializer
# This serializer handles the user preferences for spins.
# It allows users to set their preferences for product categories, price ranges, and other criteria.
class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            'dietary_restrictions',
            'allergies',
            'preferred_categories',
            'excluded_brands',
            'max_budget_default'
        ]


# Spin Item Serializer
# This serializer handles the individual items within a spin.
# It allows users to view and manage the products selected in their spins.
class SpinItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = SpinItem
        fields = ['id', 'product', 'name', 'price', 'price_unit', 'unit_price', 'quantity', 'position_in_spin', 'is_selected', 'category']

    def get_category(self, obj):
        return obj.product.category.name if obj.product and obj.product.category else None



# Spin Item Update Serializer
# This serializer is used to update the quantity of a spin item.
class SpinItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpinItem
        fields = ['quantity']




# Spin Item Select Serializer
# This serializer is used to select and deselect a spin item.
# It allows users to mark items they want to include in their final selection.
class SpinItemSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpinItem
        fields = ['id', 'is_selected', 'quantity'] # If you send {"is_selected": false}, the item will be deselected.



# Spin Serializer
# This serializer handles the spin data for the roulette feature.
# It allows users to view and manage their spins, including budget, preferences, and selected items.
class SpinSerializer(serializers.ModelSerializer):
    items = SpinItemSerializer(many=True, read_only=True,)
    preferences = UserPreferenceSerializer(read_only=True)
    preferences_snapshot = serializers.JSONField(read_only=True)
    class Meta:
        model = Spin
        fields = [
            'id', 'preferences', 'preferences_snapshot', 'budget', 'currency',
            'total_items_generated', 'total_value', 'max_items_to_select', 'status',
            'selection_started_at', 'completed_at', 'created_at', 'user', 'items'
        ]


# Create Spin Serializer
# This serializer is used to create a new spin with a budget and currency.
class CreateSpinSerializer(serializers.Serializer):
    budget = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1000)
    currency = serializers.CharField(max_length=3, default='NGN')



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